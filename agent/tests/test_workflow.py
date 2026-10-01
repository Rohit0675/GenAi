from datetime import date

from app.graph.workflow import build_workflow


def test_workflow_builds():
    workflow = build_workflow()

    assert workflow is not None


def test_workflow_runs_with_empty_evidence(monkeypatch):
    from app.graph import nodes

    def mock_retrieve_evidence(state):
        return {
            **state,
            "retrieved_documents": [],
            "retrieval_iteration_count": (
            state.get("retrieval_iteration_count", 0) + 1
        ),
        }

    monkeypatch.setattr(
        nodes,
        "retrieve_evidence",
        mock_retrieve_evidence,
    )

    workflow = build_workflow()

    state = {
        "question": "What are the recent AI updates from Figma?",
        "companies": ["Figma"],
        "date_from": date(2026, 9, 1),
        "date_to": date(2026, 9, 25),
        "category": "AI",
        "analysis_type": "recent_updates",
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

    result = workflow.invoke(state)

    assert result is not None
    assert result.get("evidence_evaluation") is not None
    assert result["evidence_evaluation"].sufficient is False