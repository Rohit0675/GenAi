from __future__ import annotations

from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL

@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)

def embed_texts(texts: list[str]):
    return get_embedding_model().encode(texts, normalize_embeddings=True, show_progress_bar=False).tolist()

def embed_query(query: str):
    return get_embedding_model().encode([query], normalize_embeddings=True, show_progress_bar=False)[0].tolist()
