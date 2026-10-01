from __future__ import annotations

from datetime import date
from typing import TypedDict

from app.schemas import (
    AnalyzeResponse,
    EvidenceEvaluation,
    InformationRequirement,
    RetrievedDocument,
)


class AgentState(TypedDict, total=False):
    # Original request
    question: str

    # Parsed parameters
    companies: list[str]
    date_from: date | None
    date_to: date | None
    category: str | None
    analysis_type: str

    # Planning
    information_requirements: list[InformationRequirement]
    retrieval_queries: list[str]

    # Evidence
    retrieved_documents: list[RetrievedDocument]
    evidence_evaluation: EvidenceEvaluation | None
    missing_information: list[str]

    # Workflow control
    retrieval_iteration_count: int

    # Analysis / synthesis
    analysis: str | None
    final_response: AnalyzeResponse | None

    # Validation / limitations
    limitations: list[str]
    validation_errors: list[str]