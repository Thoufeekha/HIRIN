

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
        views.logout_view,
        name="logout"
    ),

    path(
        "recruiter_profile_setup/",
        views.recruiter_profile_setup,
        name="recruiter_profile_setup"
    ),

    path(
        "recruiter_dashboard/",
        views.recruiter_dashboard,
        name="recruiter_dashboard"
    ),

    path(
        "post_job/",
        views.post_job,
        name="post_job"
    ),

    path(
        "job_postings/",
        views.job_postings,
        name="job_postings"
    ),

    path(
        "publish-job/<int:job_id>/",
        views.publish_job,
        name="publish_job"
    ),

    path(
        "close-job/<int:job_id>/",
        views.close_job,
        name="close_job"
    ),

    path(
        "repost-job/<int:job_id>/",
        views.repost_job,
        name="repost_job"
    ),

    path(
        "view-job/<int:job_id>/",
        views.view_job,
        name="view_job"
    ),

    path(
        "manage-jobs/",
        views.manage_jobs, 
        name="manage_jobs"
    ),

    path(
        "candidates/",
        views.candidates_list,
        name="candidates"
    ),

    path(
        "candidate/<int:candidate_id>/",
        views.candidate_profile_view,
        name="candidate_profile"
    ),

    path(
        "invite/<int:candidate_id>/",
        views.invite_candidate,
        name="invite_candidate"
    ),

    path(
        "notification/<int:invitation_id>/read/",
        views.mark_notification_read,
        name="mark_notification_read"
    ),

    path(
    "applicants/",
    views.applicants,
    name="applicants"
),

]