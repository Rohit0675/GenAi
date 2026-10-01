from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


SUPPORTED_COMPANIES = {"Figma", "Canva", "Notion"}

ANALYSIS_TYPES = {
    "recent_updates",
    "comparison",
    "feature_analysis",
    "trend_analysis",
    "executive_summary",
}


class AnalyzeRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    companies: list[str] = Field(default_factory=list, max_length=10)
    date_from: date | None = None
    date_to: date | None = None
    category: str | None = Field(default=None, max_length=100)
    analysis_type: str | None = None

    @field_validator("companies")
    @classmethod
    def validate_companies(cls, value: list[str]) -> list[str]:
        normalized = [
            company.strip()
            for company in value
            if company.strip()
        ]

        invalid = [
            company
            for company in normalized
            if company not in SUPPORTED_COMPANIES
        ]

        if invalid:
            raise ValueError(
                f"Unsupported company: {', '.join(invalid)}. "
                f"Supported companies: {', '.join(sorted(SUPPORTED_COMPANIES))}"
            )

        # Remove duplicates while preserving order
        return list(dict.fromkeys(normalized))

    @field_validator("analysis_type")
    @classmethod
    def validate_analysis_type(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return None

        normalized = value.strip().lower()

        if normalized not in ANALYSIS_TYPES:
            raise ValueError(
                f"Unsupported analysis_type: {value}. "
                f"Supported types: {', '.join(sorted(ANALYSIS_TYPES))}"
            )

        return normalized

    @field_validator("date_to")
    @classmethod
    def validate_date_range(
        cls,
        value: date | None,
        info,
    ) -> date | None:
        date_from = info.data.get("date_from")

        if (
            value is not None
            and date_from is not None
            and value < date_from
        ):
            raise ValueError(
                "date_to must be on or after date_from"
            )

        return value


class RetrievedDocument(BaseModel):
    document_id: str
    company: str
    title: str
    published_date: date
    content: str
    source_url: str
    source_type: str
    relevance_score: float = Field(ge=0.0)


class KeyFinding(BaseModel):
    company: str
    finding: str
    source_ids: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)


class SourceReference(BaseModel):
    title: str
    company: str
    published_date: date
    url: str


class AnalyzeResponse(BaseModel):
    answer: str
    analysis_type: str
    companies: list[str]
    key_findings: list[KeyFinding]
    common_themes: list[str]
    differences: list[str]
    sources: list[SourceReference]
    limitations: list[str] = Field(default_factory=list)


class InformationRequirement(BaseModel):
    description: str
    companies: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)


class EvidenceEvaluation(BaseModel):
    sufficient: bool
    missing_information: list[str] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    reasoning: str = ""


class AgentStateModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    question: str
    companies: list[str] = Field(default_factory=list)
    date_from: date | None = None
    date_to: date | None = None
    category: str | None = None
    analysis_type: str

    information_requirements: list[InformationRequirement] = Field(
        default_factory=list
    )

    retrieval_queries: list[str] = Field(
        default_factory=list
    )

    retrieved_documents: list[RetrievedDocument] = Field(
        default_factory=list
    )

    evidence_evaluation: EvidenceEvaluation | None = None

    retrieval_iteration_count: int = 0

    analysis: str | None = None

    final_response: AnalyzeResponse | None = None

    limitations: list[str] = Field(
        default_factory=list
    )

    validation_errors: list[str] = Field(
        default_factory=list
    )