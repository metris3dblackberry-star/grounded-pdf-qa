"""Build the index: python -m app.ingest"""

from __future__ import annotations

import time
from collections import Counter

from .config import settings
from .pdf_parse import parse_folder
from .store import Store


def main() -> None:
    t0 = time.perf_counter()
    chunks = parse_folder(settings.pdf_dir, settings.manifest, settings.chunk_words, settings.chunk_overlap)
    if not chunks:
        raise SystemExit(f"No PDFs with extractable text found in {settings.pdf_dir}")
    per_doc = Counter(c.title for c in chunks)
    print(f"Parsed {len(per_doc)} documents into {len(chunks)} chunks in {time.perf_counter() - t0:.1f}s")
    for title, n in per_doc.most_common():
        print(f"  {n:5d}  {title}")

    store = Store(settings)
    store.recreate()
    t1 = time.perf_counter()
    store.index(chunks)
    print(f"Indexed {store.count()} chunks into '{settings.collection}' in {time.perf_counter() - t1:.1f}s")


if __name__ == "__main__":
    main()
