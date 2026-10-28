"""Qdrant index with hybrid retrieval (dense + BM25) and cross-encoder reranking.

- Dense: BAAI/bge-small-en-v1.5 catches paraphrases ("home office" ~ "business use of home").
- Sparse: BM25 catches exact terms (form numbers like "Form 941", "Section 179").
- The two candidate lists are fused with Reciprocal Rank Fusion inside Qdrant.
- A cross-encoder then rescores (question, passage) pairs; its score also drives the
  "not in the documents" decision.

All models run locally on CPU through fastembed (ONNX), so indexing and retrieval need
no API key.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

from fastembed import SparseTextEmbedding, TextEmbedding
from fastembed.rerank.cross_encoder import TextCrossEncoder
from qdrant_client import QdrantClient, models

from .config import Settings
from .pdf_parse import Chunk

DENSE = "dense"
SPARSE = "bm25"


def contextual(payload: dict) -> str:
    """Text used for embedding and reranking: the chunk prefixed with its document title.

    Chunks lose their document context when cut out ("Your Staff ..."), so questions that
    name the document ("What does the CISA starter kit say ...") cannot match them. A short
    title header restores that link. The answer still shows the original chunk text.
    """
    return f"{payload['title']} (page {payload['page']})\n{payload['text']}"


@dataclass
class Hit:
    chunk: dict  # payload: id, doc_id, title, file, page, index, text
    fused_rank: int
    rerank_score: float


class Store:
    def __init__(self, settings: Settings):
        self.s = settings

    @cached_property
    def client(self) -> QdrantClient:
        if self.s.qdrant_url:
            return QdrantClient(url=self.s.qdrant_url)
        self.s.qdrant_path.mkdir(parents=True, exist_ok=True)
        return QdrantClient(path=str(self.s.qdrant_path))

    @cached_property
    def dense(self) -> TextEmbedding:
        return TextEmbedding(self.s.dense_model)

    @cached_property
    def sparse(self) -> SparseTextEmbedding:
        return SparseTextEmbedding(self.s.sparse_model)

    @cached_property
    def reranker(self) -> TextCrossEncoder:
        return TextCrossEncoder(self.s.rerank_model)

    def close(self) -> None:
        if "client" in self.__dict__:
            self.client.close()

    def warm_up(self) -> None:
        """Load all models up front so the first request is not slow."""
        _ = self.client, self.dense, self.sparse, self.reranker
        list(self.reranker.rerank("warm up", ["warm up"]))

    # ---------- indexing ----------

    def recreate(self) -> None:
        dim = len(next(iter(self.dense.embed(["dimension probe"]))))
        if self.client.collection_exists(self.s.collection):
            self.client.delete_collection(self.s.collection)
        self.client.create_collection(
            self.s.collection,
            vectors_config={DENSE: models.VectorParams(size=dim, distance=models.Distance.COSINE)},
            sparse_vectors_config={SPARSE: models.SparseVectorParams(modifier=models.Modifier.IDF)},
        )

    def index(self, chunks: list[Chunk], batch: int = 64) -> int:
        for start in range(0, len(chunks), batch):
            part = chunks[start:start + batch]
            texts = [contextual(c.to_payload()) for c in part]
            dense_vecs = list(self.dense.embed(texts))  # bge: passages need no prefix
            sparse_vecs = list(self.sparse.embed(texts))
            points = [
                models.PointStruct(
                    id=c.id,
                    vector={
                        DENSE: d.tolist(),
                        SPARSE: models.SparseVector(indices=s.indices.tolist(), values=s.values.tolist()),
                    },
                    payload=c.to_payload(),
                )
                for c, d, s in zip(part, dense_vecs, sparse_vecs)
            ]
            self.client.upsert(self.s.collection, points=points)
        return len(chunks)

    def count(self) -> int:
        if not self.client.collection_exists(self.s.collection):
            return 0
        return self.client.count(self.s.collection, exact=True).count

    def documents(self) -> list[dict]:
        """Distinct documents in the index with their chunk counts."""
        seen: dict[str, dict] = {}
        offset = None
        while True:
            points, offset = self.client.scroll(
                self.s.collection, limit=512, offset=offset,
                with_payload=["doc_id", "title", "file", "page"], with_vectors=False,
            )
            for p in points:
                d = seen.setdefault(p.payload["doc_id"], {
                    "doc_id": p.payload["doc_id"], "title": p.payload["title"],
                    "file": p.payload["file"], "chunks": 0, "pages": set(),
                })
                d["chunks"] += 1
                d["pages"].add(p.payload["page"])
            if offset is None:
                break
        return [{**d, "pages": len(d["pages"])} for d in sorted(seen.values(), key=lambda x: x["title"])]

    # ---------- retrieval ----------

    def hybrid(self, question: str, limit: int) -> list[dict]:
        dense_q = next(iter(self.dense.query_embed([question]))).tolist()
        sparse_q = next(iter(self.sparse.query_embed([question])))
        result = self.client.query_points(
            self.s.collection,
            prefetch=[
                models.Prefetch(query=dense_q, using=DENSE, limit=limit),
                models.Prefetch(
                    query=models.SparseVector(indices=sparse_q.indices.tolist(), values=sparse_q.values.tolist()),
                    using=SPARSE, limit=limit,
                ),
            ],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            limit=limit,
            with_payload=True,
        )
        return [p.payload for p in result.points]

    def search(self, question: str, top_k: int | None = None) -> list[Hit]:
        top_k = top_k or self.s.top_k
        candidates = self.hybrid(question, self.s.candidates)
        if not candidates:
            return []
        scores = list(self.reranker.rerank(question, [contextual(c) for c in candidates]))
        hits = [Hit(c, rank, float(score)) for rank, (c, score) in enumerate(zip(candidates, scores), start=1)]
        hits.sort(key=lambda h: h.rerank_score, reverse=True)
        return hits[:top_k]
