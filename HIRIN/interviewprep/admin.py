# interviewprep/admin.py
from django.contrib import admin
from .models import (
    InterviewSession, InterviewQuestion, InterviewAnswer,
    AptitudeTest, AptitudeQuestion, AptitudeAnswer,
    HRTip
)

@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'mode', 'created_at', 'is_completed']
    list_filter = ['mode', 'is_completed']
    search_fields = ['user__username', 'role', 'company']

@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ['session', 'order', 'difficulty', 'category']
    list_filter = ['difficulty', 'category']

@admin.register(AptitudeTest)
class AptitudeTestAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'total_questions', 'correct_answers', 'is_completed']
    list_filter = ['is_completed']

@admin.register(HRTip)
class HRTipAdmin(admin.ModelAdmin):
    list_display = ['user', 'question', 'created_at']
    search_fields = ['question']