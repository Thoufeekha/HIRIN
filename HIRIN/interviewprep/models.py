# interviewprep/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class InterviewSession(models.Model):
    """Store interview sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interview_sessions')
    company = models.CharField(max_length=200, blank=True)
    role = models.CharField(max_length=200, blank=True)
    mode = models.CharField(max_length=20, choices=[
        ('technical', 'Technical'),
        ('hr', 'HR'),
        ('mixed', 'Mixed'),
    ], default='mixed')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.role} ({self.created_at})"

class InterviewQuestion(models.Model):
    """Store interview questions"""
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    difficulty = models.CharField(max_length=20, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ], default='medium')
    category = models.CharField(max_length=100, blank=True)
    expected_points = models.JSONField(default=list, blank=True)
    evaluation_criteria = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."

class InterviewAnswer(models.Model):
    """Store user answers"""
    question = models.ForeignKey(InterviewQuestion, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.TextField()
    score = models.IntegerField(default=0)
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    suggestions = models.JSONField(default=list, blank=True)
    sample_answer = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Answer for Q{self.question.order} - Score: {self.score}"

class AptitudeTest(models.Model):
    """Store aptitude test sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='aptitude_tests')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    total_questions = models.IntegerField(default=35)
    correct_answers = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

class AptitudeQuestion(models.Model):
    """Store aptitude questions"""
    test = models.ForeignKey(AptitudeTest, on_delete=models.CASCADE, related_name='questions')
    category = models.CharField(max_length=50)
    question_text = models.TextField()
    options = models.JSONField(default=list)
    correct_answer = models.IntegerField()
    difficulty = models.CharField(max_length=20, default='medium')
    explanation = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}..."

class AptitudeAnswer(models.Model):
    """Store user aptitude answers"""
    question = models.ForeignKey(AptitudeQuestion, on_delete=models.CASCADE, related_name='answers')
    selected_answer = models.IntegerField(null=True, blank=True)
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Q{self.question.order} - Correct: {self.is_correct}"

class HRTip(models.Model):
    """Store HR interview tips"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hr_tips')
    question = models.TextField()
    best_practice = models.TextField()
    sample_answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"HR Tip for {self.user.username}"

# ============================================
# PROFILE MODEL - ADD THIS
# ============================================

class Profile(models.Model):
    """User profile with resume and job description"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    job_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"