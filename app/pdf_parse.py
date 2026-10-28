"""PDF -> clean page text -> page-bounded chunks with metadata.

Design choices:
- Chunks never cross a page boundary, so every chunk (and every answer) cites one page.
- Running headers/footers ("Publication 15 (2026)", page numbers) are detected per
  document as short lines repeated on many pages, and removed before chunking.
- Chunks are packed from whole sentences up to ~N words, with a word overlap so a fact
  that straddles two chunks is still retrievable.
"""

from __future__ import annotations

import json
import re
import uuid
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import pymupdf

NAMESPACE = uuid.UUID("6f1c7a52-2d3e-4b8e-9f0a-5c1d2e3f4a5b")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?:;])\s+(?=[A-Z0-9(\"'•])")
_BULLETS = re.compile(r"[•▪●◦]")


@dataclass
class Chunk:
    id: str
    doc_id: str
    title: str
    file: str
    page: int  # 1-based PDF page index (what a viewer's #page=N uses)
    index: int  # chunk number within the page
    text: str

    def to_payload(self) -> dict:
        return asdict(self)


def load_manifest(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    return {d["file"]: d for d in json.loads(path.read_text(encoding="utf-8"))}


def _norm_line(line: str) -> str:
    """Normalise a line for header/footer detection: digits collapse to '#'."""
    return re.sub(r"\d+", "#", line.strip().lower())


def boilerplate_lines(pages: list[list[str]], min_share: float = 0.3, max_len: int = 70) -> set[str]:
    """Short lines (normalised) that repeat on at least `min_share` of a document's pages."""
    if len(pages) < 4:
        return set()
    counts = Counter()
    for lines in pages:
        counts.update({_norm_line(l) for l in lines if l.strip() and len(l.strip()) <= max_len})
    threshold = max(3, int(len(pages) * min_share))
    return {line for line, n in counts.items() if n >= threshold}


def clean_page(lines: list[str], boilerplate: set[str]) -> str:
    kept = [l.strip() for l in lines if l.strip() and _norm_line(l) not in boilerplate]
    # Bare page numbers left over
    kept = [l for l in kept if not re.fullmatch(r"(page\s*)?\d{1,3}", l, flags=re.I)]
    text = "\n".join(kept)
    text = _BULLETS.sub("-", text)
    text = text.replace("­", "")
    # Join words hyphenated across line breaks: "employ-\nment" -> "employment"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    text = re.sub(r"\s*\n\s*", " ", text)
    return re.sub(r"\s{2,}", " ", text).strip()


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT.split(text) if s.strip()]


def pack_chunks(text: str, max_words: int, overlap: int) -> list[str]:
    """Greedy sentence packing into ~max_words chunks with ~overlap words carried over."""
    sentences = split_sentences(text)
    chunks: list[str] = []
    current: list[str] = []  # current[0] may be the carried-over overlap
    count = 0
    has_tail = False
    new_words = 0
    for sentence in sentences:
        words = sentence.split()
        # A single overlong sentence (tables, lists) is hard-split by words.
        while len(words) > max_words:
            if current:
                chunks.append(" ".join(current))
                current, count, has_tail, new_words = [], 0, False, 0
            chunks.append(" ".join(words[:max_words]))
            words = words[max_words - overlap:]
        if count + len(words) > max_words and current:
            chunks.append(" ".join(current))
            tail = " ".join(current).split()[-overlap:] if overlap else []
            current, count = ([" ".join(tail)] if tail else []), len(tail)
            has_tail, new_words = bool(tail), 0
        current.append(" ".join(words))
        count += len(words)
        new_words += len(words)
    if current:
        fresh = current[1:] if has_tail else current
        if chunks and new_words < min_tail_words(max_words):
            # A short remainder is appended to the previous chunk instead of standing alone.
            chunks[-1] = chunks[-1] + " " + " ".join(fresh)
        elif fresh:
            chunks.append(" ".join(current))
    return chunks


def min_tail_words(max_words: int) -> int:
    return max(20, max_words // 6)


def parse_pdf(path: Path, title: str, doc_id: str, max_words: int, overlap: int) -> list[Chunk]:
    doc = pymupdf.open(path)
    pages = [page.get_text().splitlines() for page in doc]
    boilerplate = boilerplate_lines(pages)
    chunks: list[Chunk] = []
    for page_no, lines in enumerate(pages, start=1):
        text = clean_page(lines, boilerplate)
        if len(text.split()) < 12:  # cover pages, blank pages, figure-only pages
            continue
        for i, piece in enumerate(pack_chunks(text, max_words, overlap)):
            cid = str(uuid.uuid5(NAMESPACE, f"{doc_id}:{page_no}:{i}"))
            chunks.append(Chunk(cid, doc_id, title, path.name, page_no, i, piece))
    return chunks


def parse_folder(pdf_dir: Path, manifest_path: Path, max_words: int, overlap: int) -> list[Chunk]:
    manifest = load_manifest(manifest_path)
    out: list[Chunk] = []
    for path in sorted(pdf_dir.glob("*.pdf")):
        meta = manifest.get(path.name, {})
        title = meta.get("title") or pymupdf.open(path).metadata.get("title") or path.stem
        doc_id = meta.get("id") or path.stem
        out.extend(parse_pdf(path, title, doc_id, max_words, overlap))
    return out
