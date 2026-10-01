from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router

app = FastAPI(
    title="Competitive Intelligence Agent",
    version="1.0.0",
)

# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# API routes
# ---------------------------------------------------------

app.include_router(
    router,
    prefix="/api",
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "competitive-intelligence-agent",
    }