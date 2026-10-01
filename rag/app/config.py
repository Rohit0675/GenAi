from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CHROMA_DIR = BASE_DIR / "chroma_db"

RAG_HOST = os.getenv("RAG_HOST", "127.0.0.1")
RAG_PORT = int(os.getenv("RAG_PORT", "8000"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "competitive_intelligence")
REQUEST_TIMEOUT_SECONDS = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
MAX_SOURCE_BYTES = int(os.getenv("MAX_SOURCE_BYTES", str(5 * 1024 * 1024)))
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "900"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "8"))
MAX_TOP_K = int(os.getenv("MAX_TOP_K", "20"))
USER_AGENT = os.getenv(
    "USER_AGENT",
    "AI-Competitive-Intelligence-RAG/1.0 (+local development; source-grounded retrieval)",
)

for path in (RAW_DIR, PROCESSED_DIR, CHROMA_DIR):
    path.mkdir(parents=True, exist_ok=True)
