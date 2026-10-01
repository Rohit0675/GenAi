from langgraph.graph import END, START, StateGraph

from app.graph import nodes
from app.graph.state import AgentState
from app.graph.synthesis import synthesize_response
from app.graph.validation import validate_output


def build_workflow():
    """
    Build the complete Competitive Intelligence Agent workflow.
    """

    graph = StateGraph(AgentState)

    # ---------------------------------------------------------
    # Nodes
    # ---------------------------------------------------------

    graph.add_node(
        "parse_request",
        nodes.parse_request,
    )

    graph.add_node(
        "plan_information_requirements",
        nodes.plan_information_requirements,
    )

    graph.add_node(
        "retrieve_evidence",
        nodes.retrieve_evidence,
    )

    graph.add_node(
        "evaluate_evidence",
        nodes.evaluate_evidence,
    )

    graph.add_node(
        "prepare_additional_retrieval",
        nodes.prepare_additional_retrieval,
    )

    graph.add_node(
        "synthesize_response",
        synthesize_response,
    )

    graph.add_node(
        "validate_output",
        validate_output,
    )

    # ---------------------------------------------------------
    # Main workflow
    # ---------------------------------------------------------

    graph.add_edge(
        START,
        "parse_request",
    )

    graph.add_edge(
        "parse_request",
        "plan_information_requirements",
    )

    graph.add_edge(
        "plan_information_requirements",
        "retrieve_evidence",
    )

    graph.add_edge(
        "retrieve_evidence",
        "evaluate_evidence",
    )

    # ---------------------------------------------------------
    # Evidence decision
    # ---------------------------------------------------------

    graph.add_conditional_edges(
        "evaluate_evidence",
        nodes.should_retrieve_more,
        {
            "continue": "synthesize_response",
            "retrieve_more": "prepare_additional_retrieval",
            "stop": "synthesize_response",
        },
    )

    # ---------------------------------------------------------
    # Additional retrieval loop
    # ---------------------------------------------------------

    graph.add_edge(
        "prepare_additional_retrieval",
        "retrieve_evidence",
    )

    # ---------------------------------------------------------
    # Synthesis → Validation → End
    # ---------------------------------------------------------

    graph.add_edge(
        "synthesize_response",
        "validate_output",
    )

    graph.add_edge(
        "validate_output",
        END,
    )

    return graph.compile()