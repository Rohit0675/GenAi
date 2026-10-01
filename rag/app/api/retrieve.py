from fastapi import APIRouter

from app.retrieval.search import semantic_search
from app.schemas import RetrieveRequest, RetrieveResponse

router = APIRouter()

@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve(request: RetrieveRequest) -> RetrieveResponse:
    results = semantic_search(
        query=request.query,
        top_k=request.top_k,
        companies=request.companies,
        date_from=request.date_from,
        date_to=request.date_to,
        category=request.category,
    )
    return RetrieveResponse(results=results)
