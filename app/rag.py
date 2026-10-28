"""The question -> answer pipeline."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field

from .config import Settings
from .llm import ClaudeAnswerer
from .store import Hit, Store
from .validate import NOT_FOUND_MESSAGE, validate


@dataclass
class Source:
    n: int
    doc_id: str
    title: str
    file: str
    page: int
    text: str
    score: float


@dataclass
class Answer:
    question: str
    found: bool
    answer: str
    sources: list[Source]
    checks: dict = field(default_factory=dict)
    timings_ms: dict = field(default_factory=dict)
    model: str | None = None
    usage: dict = field(default_factory=dict)


class RAG:
    def __init__(self, settings: Settings, store: Store | None = None, answerer=None):
        self.s = settings
        self.store = store or Store(settings)
        self._answerer = answerer
        # The embedded Qdrant store is single-process; serialise retrieval across threads.
        self._retrieval_lock = threading.Lock()

    @property
    def answerer(self):
        if self._answerer is None:
            self._answerer = ClaudeAnswerer(self.s)
        return self._answerer

    def ask(self, question: str) -> Answer:
        question = question.strip()
        t0 = time.perf_counter()
        with self._retrieval_lock:
            hits: list[Hit] = self.store.search(question)
        t_retrieval = (time.perf_counter() - t0) * 1000

        relevant = [h for h in hits if h.rerank_score >= self.s.min_rerank_score]
        best = hits[0].rerank_score if hits else None
        if not relevant:
            # Nothing in the documents is close enough: decline without calling the LLM.
            return Answer(question, False, NOT_FOUND_MESSAGE, [],
                          checks={"reason": "below_relevance_threshold", "best_score": best},
                          timings_ms={"retrieval": round(t_retrieval)})

        passages = [h.chunk for h in relevant]
        t1 = time.perf_counter()
        result = self.answerer.answer(question, passages)
        t_llm = (time.perf_counter() - t1) * 1000

        checked = validate(result.found, result.answer, result.citations, passages)
        # checked.citations holds original passage numbers in order of use; the answer text
        # has already been renumbered so that the k-th source here is [k].
        sources = [
            Source(k, passages[n - 1]["doc_id"], passages[n - 1]["title"], passages[n - 1]["file"],
                   passages[n - 1]["page"], passages[n - 1]["text"], round(relevant[n - 1].rerank_score, 2))
            for k, n in enumerate(checked.citations, start=1)
        ]
        return Answer(
            question, checked.found, checked.answer, sources,
            checks=checked.checks | {"best_score": best, "notes": result.notes},
            timings_ms={"retrieval": round(t_retrieval), "generation": round(t_llm)},
            model=result.model,
            usage={"input_tokens": result.input_tokens, "output_tokens": result.output_tokens},
        )
