from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from accounts.models import (
    RecruiterProfile,
    Job,
    Invitation
)


@login_required
def agent_invites(request, job_id):

    recruiter = RecruiterProfile.objects.get(
        user=request.user
    )

    job = get_object_or_404(
        Job,
        id=job_id,
        recruiter=recruiter
    )

    invitations = Invitation.objects.filter(
        recruiter=recruiter,
        job=job
    )

    return render(
        request,
        "recruiter/agent_invites.html",
        {
            "job": job,
            "invitations": invitations
        }
    )