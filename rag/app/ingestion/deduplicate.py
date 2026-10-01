from __future__ import annotations

import hashlib

from app.schemas import Document

def content_fingerprint(document: Document) -> str:
    normalized = " ".join(document.content.lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

def deduplicate_documents(documents: list[Document]) -> list[Document]:
    seen_ids: set[str] = set()
    seen_content: set[str] = set()
    unique = []
    for doc in documents:
        fp = content_fingerprint(doc)
        if doc.document_id in seen_ids or fp in seen_content:
            continue
        seen_ids.add(doc.document_id)
        seen_content.add(fp)
        unique.append(doc)
    return unique
