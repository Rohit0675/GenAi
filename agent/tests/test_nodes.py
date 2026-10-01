from datetime import date

from app.graph.nodes import evaluate_evidence, parse_request
from app.schemas import EvidenceEvaluation
from app.graph.state import AgentState


def test_parse_request_infers_comparison_companies_and_category():
    state: AgentState = {
        "question": "Compare the recent AI developments of Figma and Notion",
        "companies": [],
        "date_from": None,
        "date_to": None,
        "category": None,
        "analysis_type": None,
    }

    result = parse_request(state)

    assert result["companies"] == ["Figma", "Notion"]
    assert result["analysis_type"] == "comparison"
    assert result["category"] == "AI"
    assert result["date_from"] is not None
    assert result["date_to"] is not None


def test_parse_request_preserves_explicit_parameters():
    state: AgentState = {
        "question": "Recent updates",
        "companies": ["Figma"],
        "date_from": date(2026, 9, 1),
        "date_to": date(2026, 9, 24),
        "category": "AI",
        "analysis_type": "recent_updates",
    }

    result = parse_request(state)

    assert result["companies"] == ["Figma"]
    assert result["date_from"] == date(2026, 9, 1)
    assert result["date_to"] == date(2026, 9, 24)
    assert result["category"] == "AI"
    assert result["analysis_type"] == "recent_updates"


def test_parse_request_infers_feature_analysis():
    state: AgentState = {
        "question": "What AI features has Notion introduced?",
        "companies": [],
        "date_from": None,
        "date_to": None,
        "category": None,
        "analysis_type": None,
    }

    result = parse_request(state)

    assert result["companies"] == ["Notion"]
    assert result["analysis_type"] == "feature_analysis"
    assert result["category"] == "AI"


def test_evaluate_evidence_sufficient_for_all_companies():
    documents = [
        type(
            "Document",
            (),
            {
                "company": "Figma",
                "published_date": date(2026, 9, 1),
            },
        )(),
        type(
            "Document",
            (),
            {
                "company": "Notion",
                "published_date": date(2026, 9, 15),
            },
        )(),
    ]

    state: AgentState = {
        "question": "Compare Figma and Notion",
        "companies": ["Figma", "Notion"],
        "date_from": date(2026, 1, 1),
        "date_to": date(2026, 9, 25),
        "category": None,
        "analysis_type": "comparison",
        "retrieved_documents": documents,
        "limitations": [],
    }

    result = evaluate_evidence(state)

    evaluation = result["evidence_evaluation"]

    assert evaluation is not None
    assert evaluation.sufficient is True
    assert evaluation.missing_information == []


def test_evaluate_evidence_detects_missing_company():
    documents = [
        type(
            "Document",
            (),
            {
                "company": "Figma",
                "published_date": date(2026, 9, 1),
            },
        )(),
    ]

    state: AgentState = {
        "question": "Compare Figma and Canva",
        "companies": ["Figma", "Canva"],
        "date_from": date(2026, 1, 1),
        "date_to": date(2026, 9, 25),
        "category": None,
        "analysis_type": "comparison",
        "retrieved_documents": documents,
        "limitations": [],
    }

    result = evaluate_evidence(state)

    evaluation = result["evidence_evaluation"]

    assert evaluation is not None
    assert evaluation.sufficient is False
    assert "No retrieved evidence for Canva." in evaluation.missing_information