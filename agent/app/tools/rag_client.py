from __future__ import annotations

from datetime import date

import httpx

from app.config import get_settings
from app.schemas import RetrievedDocument


class RAGClientError(Exception):
    """Raised when the RAG service cannot provide usable evidence."""


class RAGClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.rag_base_url.rstrip("/")
        self.timeout = settings.rag_timeout_seconds

    def retrieve(
        self,
        query: str,
        companies: list[str] | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        category: str | None = None,
        top_k: int = 8,
    ) -> list[RetrievedDocument]:
        payload = {
            "query": query,
            "companies": companies or None,
            "date_from": date_from.isoformat() if date_from else None,
            "date_to": date_to.isoformat() if date_to else None,
            "category": category,
            "top_k": top_k,
        }

        try:
            response = httpx.post(
                f"{self.base_url}/retrieve",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise RAGClientError("RAG service request timed out.") from exc
        except httpx.HTTPStatusError as exc:
            raise RAGClientError(
                f"RAG service returned HTTP {exc.response.status_code}."
            ) from exc
        except httpx.RequestError as exc:
            raise RAGClientError(
                "RAG service is unavailable."
            ) from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise RAGClientError(
                "RAG service returned invalid JSON."
            ) from exc

        if not isinstance(data, dict) or not isinstance(
            data.get("results"), list
        ):
            raise RAGClientError(
                "RAG service returned a malformed response."
            )

        documents: list[RetrievedDocument] = []

        for item in data["results"]:
            try:
                documents.append(RetrievedDocument.model_validate(item))
            except Exception as exc:
                raise RAGClientError(
                    "RAG service returned malformed evidence."
                ) from exc

        return documents