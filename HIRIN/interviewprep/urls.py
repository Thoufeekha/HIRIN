# interviewprep/urls.py

from django.urls import path
from . import views

app_name = "interviewprep"

urlpatterns = [

    # ==========================
    # Dashboard
    # ==========================
    path("", views.interview_home, name="home"),

    # ==========================
    # Aptitude Test
    # ==========================
    path("aptitude/", views.aptitude_test, name="aptitude_test"),

    path(
        "aptitude/generate/",
        views.generate_aptitude_questions,
        name="generate_aptitude",
    ),

    path(
        "aptitude/question/<int:test_id>/",
        views.get_aptitude_question,
        name="get_aptitude_question",
    ),

    path(
        "aptitude/submit/",
        views.submit_aptitude_answer,
        name="submit_aptitude_answer",
    ),

    path(
        "aptitude/results/<int:test_id>/",
        views.aptitude_results,
        name="aptitude_results",
    ),

    # ==========================
    # Interview Practice
    # ==========================
    path(
        "interview/start/",
        views.start_interview,
        name="start_interview",
    ),

    path(
        "interview/question/<int:session_id>/",
        views.get_interview_question,
        name="get_interview_question",
    ),

    path(
        "interview/submit/",
        views.submit_interview_answer,
        name="submit_interview_answer",
    ),

    path(
        "interview/results/<int:session_id>/",
        views.interview_results,
        name="interview_results",
    ),

    # ==========================
    # HR Tips
    # ==========================
    path(
        "hr-tips/",
        views.hr_tips,
        name="hr_tips",
    ),

    # ==========================
    # Analytics
    # ==========================
    path(
        "analytics/",
        views.analytics,
        name="analytics",
    ),

    # ==========================
    # Profile
    # ==========================
    path(
        "save-profile-data/",
        views.save_profile_data,
        name="save_profile_data",
    ),

    path(
        "get-profile-data/",
        views.get_profile_data,
        name="get_profile_data",
    ),
]