from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone

from app.ingestion.sources import SourceDefinition
from app.schemas import CATEGORIES, Document

AI_TERMS = (" ai ", "artificial intelligence", "agent", "generative", "machine learning", "model", "mcp")
CATEGORY_TERMS = {
    "AI": AI_TERMS,
    "Design": ("design", "canvas", "prototype", "visual"),
    "Collaboration": ("collaborate", "team", "comment", "shared"),
    "Project Management": ("project", "roadmap", "task", "planning"),
    "Automation": ("automate", "automation", "workflow", "agent"),
    "Security": ("security", "privacy", "permission", "authentication"),
    "Integrations": ("integration", "mcp", "connector", "api"),
    "Pricing": ("pricing", "plan", "subscription", "cost"),
}

def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    return text

def classify_category(title: str, content: str, hint: str | None = None) -> str:
    if hint in CATEGORIES:
        return hint
    haystack = f" {title.lower()} {content[:5000].lower()} "
    scores = {cat: sum(haystack.count(term) for term in terms) for cat, terms in CATEGORY_TERMS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Other"

def normalize_document(source: SourceDefinition, extracted: dict) -> Document:
    published = extracted.get("published_date")
    if published is None:
        raise ValueError(f"publication date unavailable; document skipped: {source.url}")
    title = _clean(extracted["title"])
    content = _clean(extracted["content"])
    canonical = f"{source.company}|{source.product}|{source.url}|{published.isoformat()}|{content}"
    document_id = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]
    summary = content[:400].rstrip() + ("…" if len(content) > 400 else "")
    return Document(
        document_id=document_id,
        company=source.company,
        product=source.product,
        title=title,
        published_date=published,
        category=classify_category(title, content, source.category_hint),
        summary=summary,
        content=content,
        source_url=source.url,
        source_type="official",
        retrieved_at=datetime.now(timezone.utc),
    )
