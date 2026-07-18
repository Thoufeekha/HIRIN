from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
# Create your models here.



class UserRole(models.Model):

    ROLE_CHOICES = (
        ("jobseeker", "Job Seeker"),
        ("recruiter", "Recruiter"),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES
    )

    def __str__(self):
        return f"{self.user.email} - {self.role}"

class JobSeekerProfile(models.Model):

    EXPERIENCE_CHOICES = [
        ("Fresher", "Fresher"),
        ("0-2 Years", "0-2 Years"),
        ("2-5 Years", "2-5 Years"),
        ("5+ Years", "5+ Years"),
    ]

    EDUCATION_CHOICES = [
        ("Higher Secondary", "Higher Secondary"),
        ("Diploma", "Diploma"),
        ("Bachelor's Degree", "Bachelor's Degree"),
        ("Master's Degree", "Master's Degree"),
        ("PhD", "PhD"),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    phone = models.CharField(
        max_length=15
    )

    country = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    city = models.CharField(
        max_length=100
    )

    education = models.CharField(
        max_length=50,
        choices=EDUCATION_CHOICES
    )

    field = models.CharField(
        max_length=100
    )

    preferred_job_role = models.CharField(
        max_length=100
    )

    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES
    )

    skills = models.TextField()

    linkedin = models.URLField(
        blank=True,
        null=True
    )

    resume = models.FileField(
        upload_to="resumes/"
    )

    profile_completed = models.BooleanField(
        default=False
    )
    notify_job_recs = models.BooleanField(default=True)
    notify_app_updates = models.BooleanField(default=True)
    notify_newsletter = models.BooleanField(default=False)
    profile_visible = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.user.email
    
    def completeness_percent(self):
        fields = [
            self.phone,
            self.country,
            self.state,
            self.city,
            self.education,
            self.field,
            self.preferred_job_role,
            self.experience_level,
            self.skills,
            self.linkedin,
            self.resume,
        ]

        filled = sum(1 for field in fields if field)
        total = len(fields)

        return round((filled / total) * 100)

# class Company(models.Model):
#     name = models.CharField(max_length=150)
#     logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
 
#     def __str__(self):
#         return self.name
 
 
# class Job(models.Model):
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
#     title = models.CharField(max_length=150)
#     location = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     is_active = models.BooleanField(default=True)
#     posted_date = models.DateTimeField(auto_now_add=True)
 
#     def __str__(self):
#         return f"{self.title} - {self.company.name}"

class RecruiterProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    recruiter_name = models.CharField(max_length=100)

    company_name = models.CharField(max_length=200)

    company_email = models.EmailField()

    # company_website = models.URLField()

    # industry = models.CharField(max_length=100)

    # company_location = models.CharField(max_length=200)

    company_website = models.URLField(blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    company_location = models.CharField(max_length=200, blank=True, null=True)

    company_phone = models.CharField(
        max_length=20,
        blank=True
    )


    company_description = models.TextField(
        blank=True
    )

    company_logo = models.ImageField(
        upload_to="company_logos/",
        blank=True,
        null=True
    )

    profile_completed = models.BooleanField(
        default=False
    )

    total_employees = models.PositiveIntegerField(
        default=1
    )

    founded_year = models.PositiveIntegerField(
        blank=True,null=True
    )

    company_rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=5.0
    )

    candidate_agent_enabled = models.BooleanField(
        default=True
    )

class Job(models.Model):

    EMPLOYMENT_CHOICES = [
        ("Full Time", "Full Time"),
        ("Part Time", "Part Time"),
        ("Internship", "Internship"),
        ("Contract", "Contract"),
    ]

    EXPERIENCE_CHOICES = [
        ("Fresher", "Fresher"),
        ("0-2 Years", "0-2 Years"),
        ("2-5 Years", "2-5 Years"),
        ("5+ Years", "5+ Years"),
    ]

    recruiter = models.ForeignKey(
        RecruiterProfile,
        on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=200
    )

    location = models.CharField(
        max_length=200
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_CHOICES
    )

    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_CHOICES
    )

    salary = models.CharField(
        max_length=100,
        blank=True
    )

    skills = models.TextField()

    description = models.TextField()

    valid_until = models.DateField()

    is_published = models.BooleanField(
        default=False
    )

    is_closed = models.BooleanField(
    default=False
    )

    is_reposted = models.BooleanField(
        default=False
    )

    reposted_at = models.DateTimeField(
    null=True,
    blank=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    @property
    def status(self):

        if not self.is_published:
            return "Draft"

        if self.is_closed:
            return "Closed"

        today = timezone.now().date()

        if self.valid_until < today:
            return "Closed"

        elif (self.valid_until - today).days <= 3:
            return "Closing Soon"

        return "Active"

    def __str__(self):
        return self.title
 
class Application(models.Model):
    STATUS_CHOICES = [
        ("Applied", "Applied"),
        ("Viewed", "Viewed"),
        ("Shortlisted", "Shortlisted"),
        ("Interviewing", "Interviewing"),
        ("Rejected", "Rejected"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Applied"
    
    )

    last_stage = models.CharField(
    max_length=20,
    blank=True,
    null=True
    )

    

    # ADD THESE
    match_score = models.FloatField(default=0)

    matched_skills = models.TextField(
        blank=True,
        null=True
    )

    rejection_reason = models.TextField(
        blank=True,
        null=True
    )

    applied_date = models.DateTimeField(auto_now_add=True)
    status_updated_at = models.DateTimeField(auto_now=True)

    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-applied_date"]

    def __str__(self):
        return f"{self.user.email} -> {self.job.title} ({self.status})"
    

class Invitation(models.Model):

    recruiter = models.ForeignKey(
        RecruiterProfile,
        on_delete=models.CASCADE
    )

    candidate = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="invitations"
    )
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    match_score = models.FloatField(
        default=0
    )


    message = models.TextField(
        blank=True
    )

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recruiter.company_name} invited {self.candidate.email}"

class Notification(models.Model):
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    message = models.CharField(max_length=255)

    link = models.CharField(
        max_length=255,
        blank=True
    )

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.message

def notifications(request):

    if not request.user.is_authenticated:
        return {}

    items = []

    invitations = Invitation.objects.filter(
        candidate=request.user
    ).order_by("-created_at")[:10]

    for inv in invitations:
        items.append({
            "message": f"{inv.recruiter.company_name} invited you"
                       + (f" to apply for {inv.job.title}" if inv.job else ""),
            "link": reverse("mark_notification_read", args=[inv.id]),
            "is_read": inv.is_read,
            "created_at": inv.created_at,
        })

    general = Notification.objects.filter(
        recipient=request.user
    ).order_by("-created_at")[:10]

    for n in general:
        items.append({
            "message": n.message,
            "link": reverse("mark_general_notification_read", args=[n.id]),
            "is_read": n.is_read,
            "created_at": n.created_at,
        })

    items.sort(key=lambda x: x["created_at"], reverse=True)
    items = items[:10]

    unread_count = (
        Invitation.objects.filter(
            candidate=request.user,
            is_read=False
        ).count()
        +
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
    )

    return {
        "topnav_notifications": items,
        "unread_notifications_count": unread_count,
    }

    
    
    
    