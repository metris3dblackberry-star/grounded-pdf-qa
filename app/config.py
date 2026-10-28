"""Runtime settings, read from environment variables (and .env if present)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


@dataclass(frozen=True)
class Settings:
    pdf_dir: Path = field(default_factory=lambda: Path(_env("PDF_DIR", str(ROOT / "data" / "pdfs"))))
    manifest: Path = field(default_factory=lambda: Path(_env("MANIFEST", str(ROOT / "data" / "documents.json"))))

    # Qdrant: QDRANT_URL wins (server, e.g. in Docker Compose); otherwise an embedded on-disk store.
    qdrant_url: str = field(default_factory=lambda: _env("QDRANT_URL", ""))
    qdrant_path: Path = field(default_factory=lambda: Path(_env("QDRANT_PATH", str(ROOT / "data" / "qdrant"))))
    collection: str = field(default_factory=lambda: _env("COLLECTION", "docs"))

    dense_model: str = field(default_factory=lambda: _env("DENSE_MODEL", "BAAI/bge-small-en-v1.5"))
    sparse_model: str = field(default_factory=lambda: _env("SPARSE_MODEL", "Qdrant/bm25"))
    rerank_model: str = field(default_factory=lambda: _env("RERANK_MODEL", "Xenova/ms-marco-MiniLM-L-6-v2"))

    # Chunking (words)
    chunk_words: int = field(default_factory=lambda: int(_env("CHUNK_WORDS", "180")))
    chunk_overlap: int = field(default_factory=lambda: int(_env("CHUNK_OVERLAP", "40")))

    # Retrieval
    candidates: int = field(default_factory=lambda: int(_env("CANDIDATES", "30")))
    top_k: int = field(default_factory=lambda: int(_env("TOP_K", "6")))
    # Cross-encoder logit below which a passage is treated as irrelevant. If no passage
    # clears it, the bot declines without calling the LLM.
    min_rerank_score: float = field(default_factory=lambda: float(_env("MIN_RERANK_SCORE", "-2.0")))

    # Generation
    claude_model: str = field(default_factory=lambda: _env("CLAUDE_MODEL", "claude-opus-5-5"))
    effort: str = field(default_factory=lambda: _env("EFFORT", "low"))
    max_tokens: int = field(default_factory=lambda: int(_env("MAX_TOKENS", "4000")))


settings = Settings()
