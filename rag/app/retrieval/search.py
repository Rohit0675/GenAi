from __future__ import annotations

from datetime import date, datetime

from app.retrieval.embeddings import embed_query
from app.retrieval.vector_store import get_collection


def _where(companies=None, category=None):
    clauses = []

    if companies:
        clauses.append({"company": {"$in": companies}})

    if category:
        clauses.append({"category": category})

    if not clauses:
        return None

    if len(clauses) == 1:
        return clauses[0]

    return {"$and": clauses}


def _parse_date(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    return date.fromisoformat(str(value))


def semantic_search(
    query: str,
    top_k: int,
    companies=None,
    date_from=None,
    date_to=None,
    category=None,
    min_relevance: float = 0.20,
):
    collection = get_collection()

    if collection.count() == 0:
        return []

    candidate_k = min(max(top_k * 5, 50), collection.count())

    kwargs = {
        "query_embeddings": [embed_query(query)],
        "n_results": candidate_k,
        "include": ["documents", "metadatas", "distances"],
    }

    where = _where(companies, category)

    if where:
        kwargs["where"] = where

    result = collection.query(**kwargs)

    rows = []

    start_date = _parse_date(date_from)
    end_date = _parse_date(date_to)

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    for doc, metadata, distance in zip(documents, metadatas, distances):
        published_date = metadata.get("published_date")

        if start_date or end_date:
            try:
                document_date = date.fromisoformat(published_date)
            except (TypeError, ValueError):
                continue

            if start_date and document_date < start_date:
                continue

            if end_date and document_date > end_date:
                continue

        relevance_score = round(max(0.0, 1.0 - float(distance)), 6)

        if relevance_score < min_relevance:
            continue

        rows.append(
            {
                "document_id": metadata["document_id"],
                "company": metadata["company"],
                "title": metadata["title"],
                "published_date": published_date,
                "content": doc,
                "source_url": metadata["source_url"],
                "source_type": metadata["source_type"],
                "relevance_score": relevance_score,
            }
        )

        if len(rows) >= top_k:
            break

    return rows