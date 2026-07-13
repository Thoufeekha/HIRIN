from accounts.models import UserRole

from .rag import ask_question
from .rag import load_vectorstore

from .job_search import search_jobs
from .my_jobs import get_my_jobs
from .my_applications import get_my_applications
from .candidate_search import search_candidates
from .job_recommendation import recommend_jobs

vectorstore = load_vectorstore(
    "chatbot/faiss_index"
)


def get_response(query, user):

    query = query.lower().strip()

    try:
        role = UserRole.objects.get(
            user=user
        ).role

    except UserRole.DoesNotExist:
        role = None

    # ==========================
    # JOBSEEKER
    # ==========================

    if role == "jobseeker":

        if any(keyword in query for keyword in [
            "recommend jobs",
            "job recommendation",
            "suitable jobs",
            "jobs for me"
        ]):
            return (
                "Job recommendation feature is under development."
            )

        elif any(keyword in query for keyword in [
            "applied jobs",
            "applications",
            "application status"
        ]):
            return (
                "Application tracking feature is under development."
            )

        elif any(keyword in query for keyword in [
            "job",
            "jobs",
            "vacancy",
            "vacancies",
            "opening",
            "openings"
        ]):
            return search_jobs(query)

    # ==========================
    # RECRUITER
    # ==========================

    elif role == "recruiter":

        if any(keyword in query for keyword in [
            "recommend jobs",
            "job recommendation",
            "suitable jobs",
            "jobs for me"
        ]):
            return (
                "You are logged in as a recruiter. "
                "Job recommendations are available only for job seekers."
            )

        elif any(keyword in query for keyword in [
            "candidate",
            "candidates"
        ]):
            return (
                "Candidate search feature is under development."
            )

        elif any(keyword in query for keyword in [
            "recommend candidates",
            "candidate recommendation"
        ]):
            return (
                "Candidate recommendation feature is under development."
            )

        elif any(keyword in query for keyword in [
            "my jobs",
            "posted jobs",
            "active jobs"
        ]):
            return (
                "Recruiter job management feature is under development."
            )

    # ==========================
    # FALLBACK TO RAG
    # ==========================

    return ask_question(
        query,
        vectorstore
    )