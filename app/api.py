"""HTTP API and chat UI: uvicorn app.api:app"""

from __future__ import annotations

import logging
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path

import anthropic
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import settings
from .rag import RAG

log = logging.getLogger("uvicorn.error")
STATIC = Path(__file__).parent / "static"
RATE_LIMIT = 20  # questions
RATE_WINDOW = 600  # seconds, per client IP


class ChatRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


rag: RAG | None = None
_requests: dict[str, deque] = defaultdict(deque)


def get_rag() -> RAG:
    global rag
    if rag is None:
        rag = RAG(settings)
    return rag


@asynccontextmanager
async def lifespan(_: FastAPI):
    r = get_rag()
    r.store.warm_up()
    yield
    r.store.close()


app = FastAPI(title="Grounded PDF Q&A", version="1.0", lifespan=lifespan)


def _rate_limited(ip: str) -> bool:
    now = time.time()
    q = _requests[ip]
    while q and now - q[0] > RATE_WINDOW:
        q.popleft()
    if len(q) >= RATE_LIMIT:
        return True
    q.append(now)
    return False


@app.get("/api/health")
def health() -> dict:
    count = get_rag().store.count()
    return {"status": "ok" if count else "empty_index", "chunks": count, "model": settings.claude_model}


@app.get("/api/documents")
def documents() -> list[dict]:
    return get_rag().store.documents()


@app.post("/api/chat")
def chat(body: ChatRequest, request: Request) -> dict:
    ip = request.client.host if request.client else "unknown"
    if _rate_limited(ip):
        raise HTTPException(429, "Too many questions. Please wait a few minutes.")
    r = get_rag()
    if r.store.count() == 0:
        raise HTTPException(503, "The index is empty. Run `python -m app.ingest` first.")
    try:
        return asdict(r.ask(body.question))
    except anthropic.RateLimitError:
        raise HTTPException(503, "The language model is busy. Please try again in a minute.")
    except anthropic.APIConnectionError:
        raise HTTPException(503, "Could not reach the language model. Please try again.")
    except anthropic.APIStatusError as e:
        log.error("Claude API error %s (request %s): %s", e.status_code, e.request_id, e.message)
        raise HTTPException(502, "The answer service is temporarily unavailable. Please try again later.")


app.mount("/pdfs", StaticFiles(directory=settings.pdf_dir), name="pdfs")
app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC / "index.html")
