from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import PROCESSED_DIR
from app.retrieval.embeddings import embed_texts
from app.retrieval.vector_store import reset_collection
from scripts.ingest import chunk_text

def main():
    path = PROCESSED_DIR / "documents.json"
    if not path.exists():
        raise SystemExit("No processed documents. Run python scripts/ingest.py first.")
    docs = json.loads(path.read_text(encoding="utf-8"))
    collection = reset_collection()
    for doc in docs:
        chunks = chunk_text(doc["content"])
        embeddings = embed_texts(chunks)
        ids = [f"{doc['document_id']}_{i}" for i in range(len(chunks))]
        metadata = [{k: doc[k] for k in ("document_id", "company", "product", "title", "published_date", "category", "source_url", "source_type")} for _ in chunks]
        collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadata)
    print(json.dumps({"documents": len(docs), "chunks": collection.count()}, indent=2))

if __name__ == "__main__":
    main()
