from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

CATEGORIES = [
    "AI", "Design", "Collaboration", "Project Management", "Automation",
    "Security", "Integrations", "Pricing", "Other",
]

class Document(BaseModel):
    model_config = ConfigDict(extra="forbid")
    document_id: str = Field(min_length=8)
    company: str = Field(min_length=1)
    product: str = Field(min_length=1)
    title: str = Field(min_length=1)
    published_date: date
    category: Literal[
        "AI", "Design", "Collaboration", "Project Management", "Automation",
        "Security", "Integrations", "Pricing", "Other"
    ]
    summary: str = Field(min_length=1)
    content: str = Field(min_length=50)
    source_url: str = Field(min_length=8)
    source_type: Literal["official"] = "official"
    retrieved_at: datetime

class RetrieveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str = Field(min_length=1, max_length=1000)
    companies: list[str] | None = None
    date_from: date | None = None
    date_to: date | None = None
    category: str | None = None
    top_k: int = Field(default=8, ge=1, le=20)

    @field_validator("companies")
    @classmethod
    def clean_companies(cls, value):
        if value is None:
            return value
        cleaned = [v.strip() for v in value if v.strip()]
        return cleaned or None

    @field_validator("category")
    @classmethod
    def validate_category(cls, value):
        if value is None:
            return value
        if value not in CATEGORIES:
            raise ValueError(f"category must be one of: {', '.join(CATEGORIES)}")
        return value

    @field_validator("date_to")
    @classmethod
    def validate_date_range(cls, value, info):
        date_from = info.data.get("date_from")
        if value is not None and date_from is not None and value < date_from:
            raise ValueError("date_to must be greater than or equal to date_from")
        return value

class RetrievalResult(BaseModel):
    document_id: str
    company: str
    title: str
    published_date: date
    content: str
    source_url: str
    source_type: Literal["official"]
    relevance_score: float

class RetrieveResponse(BaseModel):
    results: list[RetrievalResult]
