"""Evaluate retrieval and answers on eval/questions.jsonl.

    python -m eval.run_eval                  # full run (calls Claude for answerable questions)
    python -m eval.run_eval --retrieval-only # free: retrieval metrics only, no LLM calls

Metrics
- Retrieval hit@1 / hit@k: an expected document+page is among the top reranked passages.
- Answered: the bot gave an answer (found=True) to an answerable question.
- Facts correct: every required fact (number, phrase) appears in the answer.
- Citation correct: at least one cited source is the expected document (and page, if given).
- Numbers verified: every number in the answer appears in a cited passage (code check).
- Declined: the bot said "not in the documents" for an unanswerable question.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from dataclasses import asdict
from pathlib import Path

from app.config import settings
from app.rag import RAG

HERE = Path(__file__).parent
PRICE_IN, PRICE_OUT = 4.00, 20.00  # USD per million tokens, claude-opus-5-5


def load() -> list[dict]:
    return [json.loads(line) for line in (HERE / "questions.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]


def matches(source: dict, item: dict) -> bool:
    if source["doc_id"] != item["expected_doc"]:
        return False
    return not item.get("expected_pages") or source["page"] in item["expected_pages"]


def facts_ok(answer: str, required: list[str]) -> tuple[bool, list[str]]:
    text = answer.lower()
    missing = [r for r in required if not any(alt.lower() in text for alt in r.split("|"))]
    return not missing, missing


def pct(n: int, d: int) -> str:
    return f"{n}/{d} ({100 * n / d:.0f}%)" if d else "n/a"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--retrieval-only", action="store_true")
    args = ap.parse_args()

    rag = RAG(settings)
    rag.store.warm_up()
    items = load()
    rows = []
    for item in items:
        hits = rag.store.search(item["question"])
        row = {"id": item["id"], "category": item["category"], "question": item["question"],
               "best_score": round(hits[0].rerank_score, 2) if hits else None}
        if item["category"] == "answerable":
            payloads = [h.chunk for h in hits]
            row["hit@1"] = bool(payloads) and matches(payloads[0], item)
            row[f"hit@{settings.top_k}"] = any(matches(p, item) for p in payloads)
        if not args.retrieval_only:
            t0 = time.perf_counter()
            a = rag.ask(item["question"])
            row |= {"found": a.found, "answer": a.answer, "latency_ms": round((time.perf_counter() - t0) * 1000),
                    "sources": [{"doc_id": s.doc_id, "page": s.page} for s in a.sources],
                    "checks": a.checks, "usage": a.usage}
            if item["category"] == "answerable":
                ok, missing = facts_ok(a.answer, item["must_contain"])
                row |= {"facts_ok": a.found and ok, "missing": missing,
                        "citation_ok": any(matches(s, item) for s in row["sources"]),
                        "numbers_verified": bool(a.checks.get("numbers_verified"))}
        rows.append(row)
        print(f"{row['id']}  {'found' if row.get('found') else '-----'}  "
              f"{'' if 'facts_ok' not in row else ('facts OK ' if row['facts_ok'] else 'facts MISS')}  {item['question']}")
    rag.store.close()

    ans = [r for r in rows if r["category"] == "answerable"]
    una = [r for r in rows if r["category"] == "unanswerable"]
    k = settings.top_k
    lines = [
        "# Evaluation report", "",
        f"Model: `{settings.claude_model}` (effort `{settings.effort}`) · top_k={k} · "
        f"relevance threshold={settings.min_rerank_score} · {len(ans)} answerable + {len(una)} unanswerable questions", "",
        "| Metric | Result |", "|---|---|",
        f"| Retrieval hit@1 | {pct(sum(r['hit@1'] for r in ans), len(ans))} |",
        f"| Retrieval hit@{k} | {pct(sum(r[f'hit@{k}'] for r in ans), len(ans))} |",
    ]
    if not args.retrieval_only:
        lat = [r["latency_ms"] for r in rows if "latency_ms" in r]
        tin = sum(r["usage"].get("input_tokens", 0) for r in rows)
        tout = sum(r["usage"].get("output_tokens", 0) for r in rows)
        cost = tin / 1e6 * PRICE_IN + tout / 1e6 * PRICE_OUT
        answered = [r for r in ans if r["found"]]
        lines += [
            f"| Answered (answerable questions) | {pct(len(answered), len(ans))} |",
            f"| Facts correct | {pct(sum(r['facts_ok'] for r in ans), len(ans))} |",
            f"| Citation points to the right document/page | {pct(sum(r['citation_ok'] for r in answered), len(answered))} |",
            f"| Every number verified in cited text | {pct(sum(r['numbers_verified'] for r in answered), len(answered))} |",
            f"| Declined unanswerable questions | {pct(sum(not r['found'] for r in una), len(una))} |",
            f"| …of which declined before any LLM call | {pct(sum(r['checks'].get('reason') == 'below_relevance_threshold' for r in una), len(una))} |",
            f"| Median latency | {statistics.median(lat) / 1000:.1f} s |",
            f"| LLM cost for the whole run | ${cost:.2f} ({tin:,} input + {tout:,} output tokens) |",
        ]
    lines += ["", "## Per question", "", "| ID | Question | Result |", "|---|---|---|"]
    for r in rows:
        if r["category"] == "answerable":
            res = f"hit@1 {'✓' if r['hit@1'] else '✗'} · hit@{k} {'✓' if r[f'hit@{k}'] else '✗'}"
            if "facts_ok" in r:
                res += f" · facts {'✓' if r['facts_ok'] else '✗ missing ' + ', '.join(r['missing'])}"
                res += f" · cite {'✓' if r['citation_ok'] else '✗'}"
        else:
            res = f"best score {r['best_score']}"
            if "found" in r:
                res += " · declined ✓" if not r["found"] else " · answered ✗"
        lines.append(f"| {r['id']} | {r['question']} | {res} |")

    if not args.retrieval_only:
        lines += ["", "## Answers", ""]
        for r in rows:
            lines += [f"**{r['id']}. {r['question']}**", "", f"> {r['answer']}", ""]

    report = "\n".join(lines) + "\n"
    name = "report_retrieval.md" if args.retrieval_only else "report.md"
    (HERE / name).write_text(report, encoding="utf-8")
    runs = HERE / "runs"
    runs.mkdir(exist_ok=True)
    (runs / f"{time.strftime('%Y%m%d-%H%M%S')}.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n" + "\n".join(lines[:16]))


if __name__ == "__main__":
    main()
