"""Post-generation checks. Nothing the model says is shown without passing these.

1. Citations must point at passages that were actually retrieved.
2. Inline [n] markers are reconciled with the citation list; unknown markers are removed.
3. An answer marked "found" with no valid citation is downgraded to "not found".
4. Every number in the answer (amounts, rates, years, form numbers) must appear in the
   text of at least one cited passage; numbers that do not are reported as unverified.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

_MARKER = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")
_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?")

NOT_FOUND_MESSAGE = (
    "I couldn't find this in the documents. Try rephrasing, or ask about a topic the "
    "knowledge base covers."
)


@dataclass
class Checked:
    found: bool
    answer: str
    citations: list[int]  # 1-based passage numbers, in order of first use
    checks: dict = field(default_factory=dict)


def _norm_number(raw: str) -> str:
    n = raw.replace(",", "").rstrip(".")
    if "." in n:
        n = n.rstrip("0").rstrip(".")
    return n


def numbers_in(text: str) -> set[str]:
    return {_norm_number(m) for m in _NUMBER.findall(text)}


def marker_numbers(answer: str) -> list[int]:
    out: list[int] = []
    for group in _MARKER.findall(answer):
        for n in group.split(","):
            v = int(n.strip())
            if v not in out:
                out.append(v)
    return out


def strip_invalid_markers(answer: str, valid: set[int]) -> str:
    def repl(m: re.Match) -> str:
        kept = [n.strip() for n in m.group(1).split(",") if int(n.strip()) in valid]
        return f"[{', '.join(kept)}]" if kept else ""
    return re.sub(r"\s+([.,;:])", r"\1", _MARKER.sub(repl, answer)).strip()


def validate(found: bool, answer: str, citations: list[int], passages: list[dict]) -> Checked:
    available = set(range(1, len(passages) + 1))
    used = [n for n in dict.fromkeys(marker_numbers(answer) + list(citations)) if n in available]
    invalid = sorted({n for n in marker_numbers(answer) + list(citations) if n not in available})
    answer = strip_invalid_markers(answer, set(used))
    checks: dict = {"invalid_citations_removed": invalid}

    if not found:
        if used:
            # The model could answer only part of the question: keep what it cited so the
            # partial answer stays traceable, but report it as not fully covered.
            return Checked(False, renumber(answer, used), used, checks | {"reason": "partial_answer"})
        return Checked(False, strip_invalid_markers(answer, set()) or NOT_FOUND_MESSAGE, [],
                       checks | {"reason": "model_not_found"})
    if not used:
        return Checked(False, NOT_FOUND_MESSAGE, [], checks | {"reason": "no_valid_citation"})

    # Number grounding against what the model saw for the cited passages: the passage text
    # plus its document title and page (titles carry years and publication numbers).
    cited_text = " ".join(
        f'{passages[n - 1]["title"]} {passages[n - 1]["page"]} {passages[n - 1]["text"]}' for n in used
    )
    source_numbers = numbers_in(cited_text)
    answer_wo_markers = _MARKER.sub("", answer)
    unverified = sorted(n for n in numbers_in(answer_wo_markers) if n not in source_numbers)
    checks |= {"numbers_verified": not unverified, "unverified_numbers": unverified}
    return Checked(True, renumber(answer, used), used, checks)


def renumber(answer: str, used: list[int]) -> str:
    """Rewrite markers so the k-th cited passage is shown as [k] (matches the source list)."""
    mapping = {old: new for new, old in enumerate(used, start=1)}

    def repl(m: re.Match) -> str:
        nums = [mapping[int(n.strip())] for n in m.group(1).split(",") if int(n.strip()) in mapping]
        return "".join(f"[{n}]" for n in dict.fromkeys(nums))
    return _MARKER.sub(repl, answer)
