# email_generato/models.py
from django.db import models
from django.contrib.auth.models import User

class GeneratedDocument(models.Model):
    DOCUMENT_TYPES = [
        ('cover_letter', 'Cover Letter'),
        ('cold_email', 'Cold Email'),
        ('both', 'Both'),
    ]
    
    TONE_CHOICES = [
        ('professional', 'Professional'),
        ('confident', 'Confident'),
        ('enthusiastic', 'Enthusiastic'),
        ('fresher-friendly', 'Fresher-Friendly'),
        ('experienced', 'Experienced'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Input data
    company_name = models.CharField(max_length=200)
    job_role = models.CharField(max_length=200)
    recruiter_name = models.CharField(max_length=200, blank=True)
    tone = models.CharField(max_length=20, choices=TONE_CHOICES, default='professional')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    
    # Generated content
    cover_letter_content = models.TextField(blank=True, null=True)
    cold_email_content = models.TextField(blank=True, null=True)
    
    # File paths
    cover_letter_pdf = models.FileField(upload_to='generated_docs/', blank=True, null=True)
    cover_letter_docx = models.FileField(upload_to='generated_docs/', blank=True, null=True)
    cold_email_pdf = models.FileField(upload_to='generated_docs/', blank=True, null=True)
    cold_email_docx = models.FileField(upload_to='generated_docs/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.company_name} - {self.job_role} ({self.created_at})"
    
    class Meta:
        ordering = ['-created_at']