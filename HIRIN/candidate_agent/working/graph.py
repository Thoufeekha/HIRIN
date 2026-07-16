from langgraph.graph import (
    StateGraph,
    END
)

from .state import (
    CandidateAgentState
)

from .nodes import (
    analyze_job,
    fetch_candidates,
    embedding_match,
    evaluate_candidates,
    invite_candidates,
    generate_report
)


def build_candidate_graph():

    builder = StateGraph(
        CandidateAgentState
    )

    builder.add_node(
        "analyze_job",
        analyze_job
    )

    builder.add_node(
        "fetch_candidates",
        fetch_candidates
    )

    builder.add_node(
        "embedding_match",
        embedding_match
    )

    builder.add_node(
        "evaluate_candidates",
        evaluate_candidates
    )

    builder.add_node(
        "invite_candidates",
        invite_candidates
    )

    builder.add_node(
        "generate_report",
        generate_report
    )

    builder.set_entry_point(
        "analyze_job"
    )

    builder.add_edge(
        "analyze_job",
        "fetch_candidates"
    )

    builder.add_edge(
        "fetch_candidates",
        "embedding_match"
    )

    builder.add_edge(
        "embedding_match",
        "evaluate_candidates"
    )

    builder.add_edge(
        "evaluate_candidates",
        "invite_candidates"
    )

    builder.add_edge(
        "invite_candidates",
        "generate_report"
    )

    builder.add_edge(
        "generate_report",
        END
    )

    return builder.compile()


candidate_graph = (
    build_candidate_graph()
)