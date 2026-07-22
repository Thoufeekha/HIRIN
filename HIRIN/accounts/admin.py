from django.contrib import admin
from .models import *

# ---------------------------
# Admin Branding
# ---------------------------

admin.site.site_header = "HIRIN"
admin.site.site_title = "HIRIN Admin"
admin.site.index_title = "Welcome to HIRIN Admin Panel"


# ---------------------------
# Job Seeker
# ---------------------------

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "preferred_job_role",
        "experience_level",
        "city",
        "profile_completed",
    )

    search_fields = (
        "user__username",
        "user__email",
        "preferred_job_role",
        "skills",
    )

    list_filter = (
        "experience_level",
        "education",
        "profile_completed",
    )

    ordering = ("user__username",)


# ---------------------------
# Recruiter
# ---------------------------

@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):

    list_display = (
        "company_name",
        "recruiter_name",
        "company_email",
        "candidate_agent_enabled",
        "profile_completed",
    )

    search_fields = (
        "company_name",
        "recruiter_name",
        "company_email",
    )

    list_filter = (
        "candidate_agent_enabled",
        "profile_completed",
    )

    ordering = ("company_name",)


# ---------------------------
# User Role
# ---------------------------

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "role",
    )

    list_filter = (
        "role",
    )

    search_fields = (
        "user__username",
        "user__email",
    )


# ---------------------------
# Jobs
# ---------------------------

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "recruiter",
        "location",
        "employment_type",
        "experience_level",
        "status",
        "is_published",
    )

    list_filter = (
        "employment_type",
        "experience_level",
        "is_published",
        "is_closed",
    )

    search_fields = (
        "title",
        "location",
        "skills",
        "recruiter__company_name",
    )

    ordering = (
        "-created_at",
    )


# ---------------------------
# Applications
# ---------------------------

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "job",
        "status",
        "match_score",
        "applied_date",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "user__username",
        "user__email",
        "job__title",
    )

    ordering = (
        "-applied_date",
    )



# from django.contrib import admin

# admin.site.site_header = "HIRIN Administration"
# admin.site.site_title = "HIRIN Admin"
# admin.site.index_title = "Welcome to HIRIN Admin Panel"
# # Register your models here.
# from django.contrib import admin
# from .models import *

# admin.site.register(JobSeekerProfile)
# admin.site.register(RecruiterProfile)
# admin.site.register(UserRole)
# admin.site.register(Job)
# admin.site.register(Application)