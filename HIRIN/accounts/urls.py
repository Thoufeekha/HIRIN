# accounts/urls.py

from django.urls import path
from . import views

urlpatterns = [

    path(
        'jobseeker/register/',
        views.jobseeker_register,
        name='jobseeker_register'
    ),

    path(
        'recruiter/register/',
        views.recruiter_register,
        name='recruiter_register'
    ),

    path(
    'jobseeker_profile_setup/',
    views.jobseeker_profile_setup,
    name='jobseeker_profile_setup'
    ),

]