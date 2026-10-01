from datetime import date

import httpx
import pytest

from app.tools.rag_client import RAGClient, RAGClientError


def test_rag_client_success(monkeypatch):
    payload = {
        "results": [
            {
                "document_id": "doc-1",
                "company": "Figma",
                "title": "AI Update",
                "published_date": "2026-09-20",
                "content": "Figma introduced an AI capability.",
                "source_url": "https://www.figma.com/blog/example",
                "source_type": "official",
                "relevance_score": 0.91,
            }
        ]
    }

    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return payload

    def mock_post(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(httpx, "post", mock_post)

    client = RAGClient()

    results = client.retrieve(
        query="recent AI updates",
        companies=["Figma"],
        date_from=date(2026, 9, 1),
        date_to=date(2026, 9, 24),
        category="AI",
        top_k=8,
    )

    assert len(results) == 1
    assert results[0].company == "Figma"
    assert results[0].document_id == "doc-1"


def test_rag_client_timeout(monkeypatch):
    def mock_post(*args, **kwargs):
        raise httpx.TimeoutException("timeout")

    monkeypatch.setattr(httpx, "post", mock_post)

    client = RAGClient()

    with pytest.raises(RAGClientError, match="timed out"):
        client.retrieve("recent AI updates")


def test_rag_client_unavailable(monkeypatch):
    def mock_post(*args, **kwargs):
        raise httpx.ConnectError("connection failed")

    monkeypatch.setattr(httpx, "post", mock_post)

    client = RAGClient()

    with pytest.raises(RAGClientError, match="unavailable"):
        client.retrieve("recent AI updates")


def test_rag_client_malformed_response(monkeypatch):
    class MockResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"wrong_field": []}

    def mock_post(*args, **kwargs):
        return MockResponse()

    monkeypatch.setattr(httpx, "post", mock_post)

    client = RAGClient()

    with pytest.raises(RAGClientError, match="malformed response"):
        client.retrieve("recent AI updates")