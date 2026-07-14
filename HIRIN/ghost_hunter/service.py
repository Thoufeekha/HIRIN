import os
import json
import requests

from dotenv import load_dotenv
from django.utils import timezone

from .prompt import SYSTEM_PROMPT
from .models import GhostAnalysis
from .email import (
    send_warning_email,
    send_deletion_email,
    send_admin_notification,
)

from accounts.models import Job


# Load .env
load_dotenv("Email/.env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def call_groq(job_data):
    """
    Sends job data to Groq AI and returns the analysis.
    """

    if not GROQ_API_KEY:
        raise Exception("GROQ_API_KEY not found.")

    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": json.dumps(job_data, indent=2)
            }
        ],
        "temperature": 0.3,
        "max_tokens": 300,
        "response_format": {
            "type": "json_object"
        }
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=30
    )

    response.raise_for_status()

    result = response.json()

    return json.loads(
        result["choices"][0]["message"]["content"]
    )


def analyze_job(job_id):
    """
    Analyze a job using Ghost Hunter AI.
    """

    try:
        job = Job.objects.get(id=job_id)

    except Job.DoesNotExist:
        return None

    # -------- Real values --------

    applicant_count = job.applications.count()

    days_live = (
        timezone.now().date() -
        job.created_at.date()
    ).days

    repost_count = 1 if job.is_reposted else 0

    # Replace this later when your project stores hiring statistics
    hire_rate = 100

    job_data = {
        "title": job.title,
        "description": job.description,
        "skills": job.skills,
        "location": job.location,
        "employment_type": job.employment_type,
        "salary": job.salary,

        "repost_count": repost_count,
        "applicant_count": applicant_count,
        "hire_rate": hire_rate,
        "days_live": days_live,
    }

    ai_result = call_groq(job_data)

    confidence = ai_result.get("confidence", 0)
    action = ai_result.get("action", "do_nothing")
    reasoning = ai_result.get("reasoning", "")

    if action == "auto_delete":
        status = "Deleted"

    elif action == "alert_recruiter":
        status = "Warning"

    else:
        status = "Safe"

    GhostAnalysis.objects.update_or_create(
        job=job,
        defaults={
            "confidence": confidence,
            "status": status,
            "reasoning": reasoning,
        }
    )

    # Warning case
    if action == "alert_recruiter":

        try:

            send_warning_email(
                recruiter_email=job.recruiter.company_email,
                recruiter_name=job.recruiter.recruiter_name,
                job_title=job.title,
                confidence=confidence,
                reasoning=reasoning,
            )

            send_admin_notification(
                job=job,
                confidence=confidence,
                action="WARNING",
                reasoning=reasoning,
            )

        except Exception as e:
            print("Email Error:", e)

    # Auto Delete case
    elif action == "auto_delete":

        job.is_closed = True
        job.is_published = False
        job.save()

        try:

            send_deletion_email(
                recruiter_email=job.recruiter.company_email,
                recruiter_name=job.recruiter.recruiter_name,
                job_title=job.title,
                confidence=confidence,
                reasoning=reasoning,
            )

            send_admin_notification(
                job=job,
                confidence=confidence,
                action="AUTO DELETE",
                reasoning=reasoning,
            )

        except Exception as e:
            print("Email Error:", e)

    return ai_result