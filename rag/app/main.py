from __future__ import annotations

import logging

from fastapi import FastAPI

from app.api.retrieve import router as retrieve_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title="Competitive Intelligence RAG API", version="1.0.0")
app.include_router(retrieve_router)

@app.get("/health")
def health():
    return {"status": "ok"}
