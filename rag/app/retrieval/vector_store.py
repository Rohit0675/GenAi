from __future__ import annotations

import chromadb

from app.config import CHROMA_COLLECTION, CHROMA_DIR

_client = None
_collection = None

def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        _collection = _client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection

def reset_collection():
    global _client, _collection
    client = _client or chromadb.PersistentClient(path=str(CHROMA_DIR))
    try:
        client.delete_collection(CHROMA_COLLECTION)
    except Exception:
        pass
    _client = client
    _collection = client.get_or_create_collection(
        name=CHROMA_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )
    return _collection
