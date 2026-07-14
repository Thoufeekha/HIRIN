from django.core.mail import send_mail

# Change these two emails if required
FROM_EMAIL = "hirin.project@gmail.com"
ADMIN_EMAIL = "admin@gmail.com"


def send_warning_email(recruiter_email, recruiter_name, job_title, confidence, reasoning):
    """
    Send warning email to recruiter.
    """

    subject = "HIRIN Ghost Hunter - Job Review Required"

    message = f"""
Dear {recruiter_name},

Our Ghost Hunter AI has analyzed your job posting.

Job Title:
{job_title}

Confidence Score:
{confidence}%

Reason:
{reasoning}

No action has been taken on your posting at this time.

Please review your job posting.

Regards,
HIRIN Team
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=FROM_EMAIL,
        recipient_list=[recruiter_email],
        fail_silently=False,
    )


def send_deletion_email(recruiter_email, recruiter_name, job_title, confidence, reasoning):
    """
    Notify recruiter that the job has been removed.
    """

    subject = "HIRIN Ghost Hunter - Job Automatically Removed"

    message = f"""
Dear {recruiter_name},

Our Ghost Hunter AI has analyzed your job posting.

Job Title:
{job_title}

Confidence Score:
{confidence}%

Reason:
{reasoning}

Since the confidence score is very high, your job posting has been automatically removed from HIRIN.

If you believe this was a mistake, please contact the administrator.

Regards,
HIRIN Team
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=FROM_EMAIL,
        recipient_list=[recruiter_email],
        fail_silently=False,
    )


def send_admin_notification(job, confidence, action, reasoning):
    """
    Notify admin about Ghost Hunter decision.
    """

    subject = f"Ghost Hunter Alert - {action}"

    message = f"""
Ghost Hunter has completed an analysis.

Job Title:
{job.title}

Recruiter:
{job.recruiter.recruiter_name}

Company:
{job.recruiter.company_name}

Confidence:
{confidence}%

Action:
{action}

Reason:
{reasoning}
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=FROM_EMAIL,
        recipient_list=[ADMIN_EMAIL],
        fail_silently=False,
    )