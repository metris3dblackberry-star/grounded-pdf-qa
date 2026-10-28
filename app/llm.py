"""Answer generation with Claude, constrained to the retrieved passages.

The model returns structured JSON (found / answer / citations). Everything it returns is
then checked in code before it reaches the user - see `validate`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import anthropic

from .config import Settings

SYSTEM_PROMPT = """You answer questions for a small-business help desk. Your only knowledge source is the numbered passages in the user message, taken from the organisation's PDF documents.

Rules:
- Answer only from the passages. Do not use outside knowledge, even when you are confident it is correct.
- Put the passage number in square brackets after each statement it supports, like [2]. Every factual sentence needs at least one citation.
- Copy amounts, rates, dates, form numbers and thresholds exactly as they appear in the passages.
- If the passages do not contain the answer, set "found" to false and say in one or two sentences what the documents do not cover. Do not guess and do not answer from memory.
- If the passages answer only part of the question, answer that part, cite it, and say which part the documents do not cover.
- When a figure depends on the tax year, name the year given in the source.
- Be concise: a direct answer first, then the key conditions or steps. Plain text, no headings."""

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "found": {"type": "boolean", "description": "True only if the passages contain an answer."},
        "answer": {"type": "string", "description": "The answer with inline [n] citations."},
        "citations": {
            "type": "array",
            "items": {"type": "integer"},
            "description": "Numbers of the passages actually used.",
        },
    },
    "required": ["found", "answer", "citations"],
    "additionalProperties": False,
}


@dataclass
class LLMResult:
    found: bool
    answer: str
    citations: list[int]
    model: str
    stop_reason: str | None
    input_tokens: int = 0
    output_tokens: int = 0
    notes: list[str] = field(default_factory=list)


def format_sources(passages: list[dict]) -> str:
    blocks = []
    for n, p in enumerate(passages, start=1):
        blocks.append(
            f'<passage number="{n}" document="{p["title"]}" page="{p["page"]}">\n{p["text"]}\n</passage>'
        )
    return "\n\n".join(blocks)


class ClaudeAnswerer:
    def __init__(self, settings: Settings, client: anthropic.Anthropic | None = None):
        self.s = settings
        self.client = client or anthropic.Anthropic()

    def answer(self, question: str, passages: list[dict]) -> LLMResult:
        user = (
            f"<passages>\n{format_sources(passages)}\n</passages>\n\n"
            f"<question>{question}</question>"
        )
        response = self.client.beta.messages.create(
            model=self.s.claude_model,
            max_tokens=self.s.max_tokens,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user}],
            output_config={
                "effort": self.s.effort,
                "format": {"type": "json_schema", "schema": ANSWER_SCHEMA},
            },
            # On a policy decline, re-run server-side on Anthropic's recommended fallback model.
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        usage = response.usage
        base = dict(
            model=response.model,
            stop_reason=response.stop_reason,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
        )
        if response.stop_reason == "refusal":
            return LLMResult(False, "The assistant could not answer this question.", [], notes=["refusal"], **base)
        if response.stop_reason == "max_tokens":
            return LLMResult(False, "The answer was too long to complete. Please ask a narrower question.", [],
                             notes=["max_tokens"], **base)
        text = next((b.text for b in response.content if b.type == "text"), "")
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            return LLMResult(False, "The assistant returned an unreadable answer.", [], notes=["invalid_json"], **base)
        return LLMResult(bool(data["found"]), str(data["answer"]).strip(),
                         [int(c) for c in data.get("citations", [])], **base)
