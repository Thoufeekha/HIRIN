

from django.urls import path


from . import views

urlpatterns = [

    path(
        'jobseeker/register/',
        views.jobseeker_register,
        name='jobseeker_register'
    ),

    path(
        'login/',
        views.jobseeker_login,
        name='jobseeker_login'
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

    path(
        "profile/",
        views.jobseeker_profile,
        name="jobseeker_profile"
    ),

    path(
        "jobseeker_dashboard/",
        views.jobseeker_dashboard,
        name="jobseeker_dashboard"
    ),

    path(
        "job_tracker/",
        views.job_tracker,
        name="job_tracker"
    ),

    
    path(
        "job-tracker/update/<int:application_id>/", 
         views.update_application_status,
        name="update_application_status"
    ),

 

    path(
    "add-job/",
    views.add_job,
    name="add_job"
   ),

    path(
        "jobs/",
        views.job_list,
        name="job_list"
    ),

    path(
        "apply/<int:job_id>/",
        views.apply_job,
        name="apply_job"
    ),

    path(
        "ats_resume/",
        views.ats_resume,
        name="ats_resume"
    ),

    path(
    "email_generator/",
    views.email_generator,
    name="email_generator"
    ),

    path(
        "cover_letter/",
        views.cover_letter,
        name="cover_letter"
    ),

    path(
        "interview_prep/",
        views.interview_prep,
        name="interview_prep"
    ),

    path(
        "logout/",
        views.jobseeker_logout,
        name="logout"
    ),

]