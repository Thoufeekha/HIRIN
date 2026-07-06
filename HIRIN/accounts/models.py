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

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.user.email