from datetime import date, datetime, timezone

import pytest

from app.ingestion.deduplicate import deduplicate_documents
from app.ingestion.normalize import normalize_document
from app.schemas import Document, RetrieveRequest
from app.ingestion.sources import SourceDefinition


def make_doc(doc_id="12345678"):
    return Document(
        document_id=doc_id,
        company="Figma",
        product="Figma",
        title="AI update",
        published_date=date(2026, 9, 1),
        category="AI",
        summary="A summary",
        content="This is sufficiently long content describing an AI product update from an official source. " * 2,
        source_url="https://example.com/a",
        source_type="official",
        retrieved_at=datetime.now(timezone.utc),
    )

def test_document_schema_validates():
    assert make_doc().company == "Figma"

def test_invalid_category_rejected():
    with pytest.raises(Exception):
        RetrieveRequest(query="x", category="NotARealCategory")

def test_top_k_bounded():
    with pytest.raises(Exception):
        RetrieveRequest(query="x", top_k=21)

def test_date_range_validated():
    with pytest.raises(Exception):
        RetrieveRequest(query="x", date_from=date(2026, 9, 2), date_to=date(2026, 9, 1))

def test_deduplicate():
    d = make_doc()
    assert len(deduplicate_documents([d, d])) == 1

def test_normalization_rejects_missing_date():
    source = SourceDefinition("Figma", "Figma", "https://example.com", category_hint="AI")
    with pytest.raises(ValueError):
        normalize_document(source, {"title": "x", "published_date": None, "content": "long " * 100})
