from accounts.models import Application

def get_my_applications(user):

    applications = Application.objects.filter(
        user=user
    )

    if not applications.exists():
        return "You haven't applied for any jobs yet."

    response = "Your applications:\n\n"

    for app in applications:

        response += (
            f"🔹 {app.job.title}\n"
            f"🏢 {app.job.recruiter.company_name}\n"
            f"📌 {app.status}\n\n"
        )

    return response