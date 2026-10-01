from __future__ import annotations

from datetime import date, timedelta

from app.schemas import InformationRequirement
from app.graph.state import AgentState


def _resolve_default_dates(
    date_from: date | None = None,
    date_to: date | None = None,
) -> tuple[date | None, date | None]:
    """
    Preserve user-supplied dates.

    If no dates are supplied, do not impose an artificial
    30-day restriction.
    """
    return date_from, date_to


def parse_request(state: AgentState) -> AgentState:
    """
    Normalize a natural-language request into structured Agent state.

    Explicit API parameters are preserved.
    Missing companies, analysis type, and category are inferred
    from the user's question using deterministic rules.
    """

    question = state["question"].strip()
    question_lower = question.lower()

    # ---------------------------------------------------------
    # 1. Companies
    # ---------------------------------------------------------
    explicit_companies = state.get("companies", [])

    if explicit_companies:
        companies = explicit_companies
    else:
        detected_companies = []

        for company in ("Figma", "Canva", "Notion"):
            if company.lower() in question_lower:
                detected_companies.append(company)

        companies = detected_companies

    # ---------------------------------------------------------
    # 2. Analysis type
    # ---------------------------------------------------------
    analysis_type = state.get("analysis_type")

    if analysis_type:
        analysis_type = analysis_type.strip().lower()
    else:
        if any(
            keyword in question_lower
            for keyword in (
                "compare",
                "comparison",
                "versus",
                "vs ",
                "difference",
                "differences",
            )
        ):
            analysis_type = "comparison"

        elif any(
            keyword in question_lower
            for keyword in (
                "feature",
                "features",
                "capability",
                "capabilities",
            )
        ):
            analysis_type = "feature_analysis"

        elif any(
            keyword in question_lower
            for keyword in (
                "trend",
                "trends",
                "over time",
                "growth",
            )
        ):
            analysis_type = "trend_analysis"

        elif any(
            keyword in question_lower
            for keyword in (
                "summary",
                "summarize",
                "overview",
                "executive",
            )
        ):
            analysis_type = "executive_summary"

        else:
            analysis_type = "recent_updates"

    # ---------------------------------------------------------
    # 3. Category
    # ---------------------------------------------------------
    category = state.get("category")

    if category is None:
        category_keywords = {
            "AI": (
                "ai",
                "artificial intelligence",
                "machine learning",
                "generative ai",
                "genai",
            ),
            "Product": (
                "product",
                "product update",
                "product updates",
                "new product",
                "new products",
            ),
            "Technology": (
                "technology",
                "technology updates",
                "tech",
            ),
        }

        for category_name, keywords in category_keywords.items():
            if any(keyword in question_lower for keyword in keywords):
                category = category_name
                break

    # ---------------------------------------------------------
    # 4. Date range
    # ---------------------------------------------------------
    date_from = state.get("date_from")
    date_to = state.get("date_to")

    if date_from is None or date_to is None:
        default_from, default_to = _resolve_default_dates()

        if date_from is None:
            date_from = default_from

        if date_to is None:
            date_to = default_to

    # ---------------------------------------------------------
    # 5. Information requirements
    # ---------------------------------------------------------
    requirements = [
        InformationRequirement(
            description=question,
            companies=companies,
            topics=[category] if category else [],
        )
    ]

    # ---------------------------------------------------------
    # 6. Retrieval queries
    # ---------------------------------------------------------
    if analysis_type == "comparison" and companies:
        retrieval_queries = [
            f"{question} for {company}"
            for company in companies
        ]
    else:
        retrieval_queries = [question]

    # ---------------------------------------------------------
    # 7. Return normalized state
    # ---------------------------------------------------------
    return {
        **state,
        "question": question,
        "companies": companies,
        "date_from": date_from,
        "date_to": date_to,
        "category": category,
        "analysis_type": analysis_type,
        "information_requirements": requirements,
        "retrieval_queries": retrieval_queries,
        "retrieval_iteration_count": 0,
        "limitations": state.get("limitations", []),
        "validation_errors": state.get("validation_errors", []),
    }
def plan_information_requirements(state: AgentState) -> dict:
    companies = state.get("companies", [])
    category = state.get("category")
    analysis_type = state.get("analysis_type", "comparison")

    requirements = []
    queries = []

    if analysis_type == "comparison":
        for company in companies:
            topic = category or "recent developments"

            requirements.append(
                InformationRequirement(
                    description=f"Recent {topic} developments for {company}",
                    companies=[company],
                    topics=[topic],
                )
            )

            queries.append(
                f"{company} recent {topic} developments"
            )

    else:
        topic = category or "recent developments"

        requirements.append(
            InformationRequirement(
                description=f"Recent {topic} developments",
                companies=companies,
                topics=[topic],
            )
        )

        queries.append(
            f"{' '.join(companies)} recent {topic} developments"
        )

    return {
        "information_requirements": requirements,
        "retrieval_queries": queries,
    }
from app.tools.rag_client import RAGClient, RAGClientError


def retrieve_evidence(state: AgentState) -> AgentState:
    """
    Retrieve evidence from the external RAG service.

    Each planned query is sent to RAG. Results are merged and
    duplicate document/chunk IDs are removed.
    """
    client = RAGClient()

    existing_documents = {
        document.document_id: document
        for document in state.get("retrieved_documents", [])
    }

    queries = state.get("retrieval_queries", [])

    if not queries:
        queries = [state["question"]]

    errors: list[str] = []

    for query in queries:
        try:
            documents = client.retrieve(
                query=query,
                companies=state.get("companies"),
                date_from=state.get("date_from"),
                date_to=state.get("date_to"),
                category=state.get("category"),
                top_k=5,
            )

            for document in documents:
                existing_documents[document.document_id] = document

        except RAGClientError as exc:
            errors.append(str(exc))

    limitations = list(state.get("limitations", []))

    if errors:
        limitations.extend(errors)

    return {
        **state,
        "retrieved_documents": list(existing_documents.values()),
        "retrieval_iteration_count": (
            state.get("retrieval_iteration_count", 0) + 1
        ),
        "limitations": limitations,
    }
from app.schemas import EvidenceEvaluation


def evaluate_evidence(state: AgentState) -> AgentState:
    """
    Evaluate whether the retrieved evidence is sufficient for the request.
    This is a deterministic first-pass evaluator; the LLM analysis comes later.
    """
    documents = state.get("retrieved_documents", [])
    requested_companies = set(state.get("companies", []))
    date_from = state.get("date_from")
    date_to = state.get("date_to")
    category = state.get("category")

    missing_information: list[str] = []
    conflicts: list[str] = []

    # 1. Check whether we have any evidence.
    if not documents:
        missing_information.append(
            "No relevant evidence was retrieved from the RAG service."
        )

    # 2. Check requested companies.
# Normalize company names to avoid false "missing company" results
# caused by capitalization or surrounding whitespace.
    retrieved_companies_normalized = {
    doc.company.strip().casefold()
    for doc in documents
}

    for company in requested_companies:
        if company.strip().casefold() not in retrieved_companies_normalized:
            missing_information.append(
            f"No retrieved evidence for {company}."
        )

    # 3. Check date range.
    date_valid_documents = []

    for document in documents:
        if date_from and document.published_date < date_from:
            continue

        if date_to and document.published_date > date_to:
            continue

        date_valid_documents.append(document)

    if documents and not date_valid_documents:
        missing_information.append(
            "Retrieved evidence does not fall within the requested date range."
        )

    # 4. Check category coverage.
    #
    # The RAG response currently does not expose a structured category field,
    # so we do not invent category information. We only record that category
    # verification is limited when a category was requested.
    if category and documents:
        limitations = list(state.get("limitations", []))

        category_note = (
            f"Category '{category}' could not be independently verified "
            "from a structured category field in the RAG response."
        )

        if category_note not in limitations:
            limitations.append(category_note)

        state = {
            **state,
            "limitations": limitations,
        }

    # 5. Determine sufficiency.
    sufficient = len(missing_information) == 0

    evaluation = EvidenceEvaluation(
        sufficient=sufficient,
        missing_information=missing_information,
        conflicts=conflicts,
        reasoning=(
            "Evidence is sufficient for the current retrieval requirements."
            if sufficient
            else "Additional evidence may be required to cover the identified gaps."
        ),
    )

    return {
        **state,
        "evidence_evaluation": evaluation,
        "missing_information": missing_information,
    }
def prepare_additional_retrieval(state: AgentState) -> AgentState:
    """
    Build targeted retrieval queries from the evidence gaps.
    """
    missing = state.get("missing_information", [])
    companies = state.get("companies", [])
    question = state["question"]

    queries = []

    for gap in missing:
        if companies:
            for company in companies:
                queries.append(
                    f"{question}. Specifically find evidence for {company}: {gap}"
                )
        else:
            queries.append(
                f"{question}. Specifically find evidence about: {gap}"
            )

    if not queries:
        queries = [question]

    return {
        **state,
        "retrieval_queries": queries,
    }


from app.config import get_settings


def should_retrieve_more(state: AgentState) -> str:
    """
    Decide whether the workflow should synthesize the response,
    perform another targeted retrieval, or stop due to the
    maximum retrieval iteration limit.
    """

    evaluation = state.get("evidence_evaluation")
    iteration_count = state.get("retrieval_iteration_count", 0)

    settings = get_settings()
    max_iterations = settings.max_retrieval_iterations

    # If evidence is already sufficient, go directly to synthesis.
    if evaluation is not None and evaluation.sufficient:
        return "continue"

    # If evidence is insufficient but we have already reached
    # the maximum number of retrieval attempts, stop and synthesize
    # an insufficient-evidence response.
    if iteration_count >= max_iterations:
        return "stop"

    # Otherwise, perform one more targeted retrieval.
    return "retrieve_more"