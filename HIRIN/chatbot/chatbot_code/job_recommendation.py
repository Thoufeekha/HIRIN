from accounts.models import JobSeekerProfile
from accounts.models import Job

def recommend_jobs(user):

    try:
        profile = JobSeekerProfile.objects.get(
            user=user
        )

    except JobSeekerProfile.DoesNotExist:
        return "Please complete your profile first."

    jobs = Job.objects.filter(
        title__icontains=profile.preferred_job_role
    )[:5]

    if not jobs.exists():
        return "No matching jobs found."

    response = "Recommended jobs:\n\n"

    for job in jobs:

        response += (
            f"🔹 {job.title}\n"
            f"🏢 {job.recruiter.company_name}\n"
            f"📍 {job.location}\n\n"
        )

    return response