from typing import TypedDict


class CandidateAgentState(TypedDict):

    # Input
    job_id: int

    # Job information
    job_data: dict

    # All retrieved candidates
    candidates: list

    # Top candidates after embedding similarity
    top_candidates: list

    # LLM evaluated candidates
    evaluations: list

    # Candidates finally invited
    invited_candidates: list

    # Summary report for recruiter
    report: str