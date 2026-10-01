from fastapi import APIRouter, HTTPException

from app.graph.workflow import build_workflow
from app.schemas import AnalyzeRequest, AnalyzeResponse

router = APIRouter()

workflow = build_workflow()


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(request: AnalyzeRequest):
    try:
        initial_state = {
            "question": request.question,
            "companies": request.companies,
            "date_from": request.date_from,
            "date_to": request.date_to,
            "category": request.category,
            "analysis_type": request.analysis_type,
            "information_requirements": [],
            "retrieval_queries": [],
            "retrieved_documents": [],
            "evidence_evaluation": None,
            "missing_information": [],
            "retrieval_iteration_count": 0,
            "analysis": None,
            "final_response": None,
            "limitations": [],
            "validation_errors": [],
        }

        result = workflow.invoke(initial_state)

        if result.get("final_response") is None:
            errors = result.get("validation_errors", [])
            detail = "; ".join(errors) if errors else "Agent failed to produce a response."
            raise HTTPException(status_code=502, detail=detail)

        if result.get("validation_errors"):
            raise HTTPException(
                status_code=502,
                detail="; ".join(result["validation_errors"]),
            )

        return result["final_response"]

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {exc}",
        )