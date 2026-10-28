"""API tests with fake retrieval and a fake LLM: no models, no index, no API key."""

import pytest
from fastapi.testclient import TestClient

import app.api as api
from app.config import Settings
from app.llm import LLMResult
from app.rag import RAG
from app.store import Hit

CHUNK = {"id": "x", "doc_id": "irs-p15", "title": "IRS Publication 15 (2026)", "file": "irs-p15.pdf",
         "page": 2, "index": 0, "text": "The social security wage base limit is $184,500."}


class FakeStore:
    def __init__(self, score):
        self.score = score

    def warm_up(self):
        pass

    def close(self):
        pass

    def count(self):
        return 1

    def documents(self):
        return [{"doc_id": "irs-p15", "title": CHUNK["title"], "file": CHUNK["file"], "chunks": 1, "pages": 1}]

    def search(self, question, top_k=None):
        return [Hit(CHUNK, 1, self.score)]


class FakeAnswerer:
    calls = 0

    def answer(self, question, passages):
        FakeAnswerer.calls += 1
        return LLMResult(True, "The 2026 wage base is $184,500 [1].", [1], "fake-model", "end_turn", 100, 20)


@pytest.fixture
def client_factory(monkeypatch):
    def make(score: float):
        FakeAnswerer.calls = 0
        monkeypatch.setattr(api, "rag", RAG(Settings(), store=FakeStore(score), answerer=FakeAnswerer()))
        api._requests.clear()
        return TestClient(api.app)
    return make


def test_health_and_documents(client_factory):
    with client_factory(5.0) as c:
        assert c.get("/api/health").json()["status"] == "ok"
        assert c.get("/api/documents").json()[0]["doc_id"] == "irs-p15"


def test_chat_returns_grounded_answer_with_sources(client_factory):
    with client_factory(5.0) as c:
        data = c.post("/api/chat", json={"question": "What is the wage base?"}).json()
    assert data["found"] is True
    assert data["sources"][0]["page"] == 2
    assert data["checks"]["numbers_verified"] is True


def test_irrelevant_question_is_declined_without_llm_call(client_factory):
    with client_factory(-9.0) as c:
        data = c.post("/api/chat", json={"question": "What is the capital of France?"}).json()
    assert data["found"] is False
    assert data["checks"]["reason"] == "below_relevance_threshold"
    assert FakeAnswerer.calls == 0


def test_question_length_is_validated(client_factory):
    with client_factory(5.0) as c:
        assert c.post("/api/chat", json={"question": "x" * 501}).status_code == 422
        assert c.post("/api/chat", json={"question": ""}).status_code == 422


def test_rate_limit(client_factory):
    with client_factory(5.0) as c:
        codes = [c.post("/api/chat", json={"question": "What is the wage base?"}).status_code
                 for _ in range(api.RATE_LIMIT + 1)]
    assert codes[-1] == 429 and codes[0] == 200


def test_index_page_is_served(client_factory):
    with client_factory(5.0) as c:
        r = c.get("/")
    assert r.status_code == 200 and "Grounded PDF Q&amp;A" in r.text
