from accounts.models import RecruiterProfile, Job

def get_my_jobs(user):

    try:
        recruiter = RecruiterProfile.objects.get(
            user=user
        )

    except RecruiterProfile.DoesNotExist:
        return "Recruiter profile not found."

    jobs = Job.objects.filter(
        recruiter=recruiter
    )

    if not jobs.exists():
        return "You haven't posted any jobs yet."

    response = "Your jobs:\n\n"

    for job in jobs:

        response += (
            f"🔹 {job.title}\n"
            f"📍 {job.location}\n"
            f"📌 {job.status}\n\n"
        )

    return response