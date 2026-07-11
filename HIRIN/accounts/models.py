from django.db import models
from django.contrib.auth.models import User

# Create your models here.

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

class Company(models.Model):
    name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
 
    def __str__(self):
        return self.name
 
 
class Job(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=150)
    location = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    posted_date = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.title} - {self.company.name}"
 
 
class Application(models.Model):
    STATUS_CHOICES = [
        ("Applied", "Applied"),
        ("Shortlisted", "Shortlisted"),
        ("Interviewing", "Interviewing"),
        ("Rejected", "Rejected"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Applied")
    applied_date = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        ordering = ["-applied_date"]
 
    def __str__(self):
        return f"{self.user.email} -> {self.job.title} ({self.status})"