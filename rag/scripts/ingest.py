from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import PROCESSED_DIR, RAW_DIR
from app.ingestion.deduplicate import deduplicate_documents
from app.ingestion.extract import extract_source
from app.ingestion.fetch import SourceFetchError, fetch_source
from app.ingestion.normalize import normalize_document
from app.ingestion.sources import SOURCES
from app.retrieval.embeddings import embed_texts
from app.retrieval.vector_store import get_collection

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger("ingest")

def chunk_text(text: str, size: int = 900, overlap: int = 120):
    if size <= overlap:
        raise ValueError("chunk size must be greater than overlap")
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + size)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end == len(text):
            break
        start = end - overlap
    return chunks

def main():
    documents = []
    failures = []
    for source in SOURCES:
        log.info("Fetching %s", source.url)
        try:
            fetched = fetch_source(source)
            raw_path = RAW_DIR / f"{source.company.lower()}_{fetched.content_hash[:12]}.html"
            raw_path.write_bytes(fetched.body)
            extracted = extract_source(fetched)
            doc = normalize_document(source, extracted)
            documents.append(doc)
        except Exception as exc:
            log.error("Source failed: %s", exc)
            failures.append({"url": source.url, "error": str(exc)})

    unique = deduplicate_documents(documents)
    processed_path = PROCESSED_DIR / "documents.json"
    processed_path.write_text(json.dumps([d.model_dump(mode="json") for d in unique], indent=2), encoding="utf-8")

    collection = get_collection()
    existing_ids = set(collection.get(include=["metadatas"]).get("ids", []))
    added = 0
    for doc in unique:
        chunks = chunk_text(doc.content)
        embeddings = embed_texts(chunks)
        ids = [f"{doc.document_id}_{i}" for i in range(len(chunks))]
        metadata = [{
            "document_id": doc.document_id,
            "company": doc.company,
            "product": doc.product,
            "title": doc.title,
            "published_date": doc.published_date.isoformat(),
            "category": doc.category,
            "source_url": doc.source_url,
            "source_type": doc.source_type,
        } for _ in chunks]
        new = [(i, c, e, m) for i, c, e, m in zip(ids, chunks, embeddings, metadata) if i not in existing_ids]
        if new:
            collection.add(
                ids=[x[0] for x in new],
                documents=[x[1] for x in new],
                embeddings=[x[2] for x in new],
                metadatas=[x[3] for x in new],
            )
            added += len(new)

    report = {"sources_configured": len(SOURCES), "documents_valid": len(unique), "chunks_added": added, "failures": failures}
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
