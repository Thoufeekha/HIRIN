from accounts.models import JobSeekerProfile

def search_candidates(query):

    skills = query.lower()

    candidates = JobSeekerProfile.objects.filter(
        skills__icontains=skills
    )[:5]

    if not candidates:
        return "No matching candidates found."

    response = "Matching candidates:\n\n"

    for candidate in candidates:

        response += (
            f"👤 {candidate.user.first_name}\n"
            f"🛠 {candidate.skills[:100]}\n\n"
        )

    return response