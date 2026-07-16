from .graph import (
    candidate_graph
)


def run_candidate_graph(job_id):

    initial_state = {

        "job_id": job_id,

        "job_data": {},

        "candidates": [],

        "top_candidates": [],

        "evaluations": [],

        "invited_candidates": [],

        "report": ""
    }

    result = candidate_graph.invoke(
        initial_state
    )

    return result