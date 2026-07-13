from accounts.models import JobSeekerProfile


def recommend_candidates(job):

    candidates = JobSeekerProfile.objects.all()

    recommendations = []

    job_skills = [
        s.strip().lower()
        for s in job.skills.split(",")
    ]

    for candidate in candidates:

        candidate_skills = [
            s.strip().lower()
            for s in candidate.skills.split(",")
        ]

        matched = len(
            set(job_skills)
            &
            set(candidate_skills)
        )

        score = (
            matched
            /
            max(len(job_skills), 1)
        ) * 100

        recommendations.append(
            (candidate, round(score))
        )

    recommendations.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return recommendations[:5]