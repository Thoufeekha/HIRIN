from accounts.models import Job


def search_jobs(query):

    jobs = Job.objects.filter(
        is_published=True,
        is_closed=False
    )

    query = query.lower()

    # Search by location
    if "in " in query:

        location = query.split("in ")[-1].strip()

        jobs = jobs.filter(
            location__icontains=location
        )

    jobs = jobs[:5]

    if not jobs.exists():
        return "No matching jobs found."

    response = "Here are some jobs:\n\n"

    for job in jobs:

        response += (
            f"🔹 {job.title}\n"
            f"🏢 {job.recruiter.company_name}\n"
            f"📍 {job.location}\n"
            f"💼 {job.employment_type}\n\n"
        )

    return response