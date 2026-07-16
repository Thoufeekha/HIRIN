
from django.db.models import Q
from django.shortcuts import  render,redirect,get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.contrib.auth import login,logout
from .models import JobSeekerProfile, RecruiterProfile, UserRole, Job,Invitation,Application,Notification,Job,RecruiterProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate
from django.utils import timezone
from django.urls import reverse
from candidate_agent.working.agent import run_candidate_graph

# Create your views here.
def jobseeker_register(request):

    if request.method == "POST":

        fullname = request.POST.get("fullname")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:

            return render(
                request,
                "jobseeker_register.html",
                {"error": "Passwords do not match"}
            )

        if User.objects.filter(email=email).exists():

            return render(
                request,
                "jobseeker_register.html",
                {"error": "Email already exists"}
            )

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=fullname
        )

        UserRole.objects.create(
            user=user,
            role="jobseeker"
        )

        # Automatically log user in
        login(request, user)

        # Send them to profile setup
        return redirect("jobseeker_profile_setup")

    return render(
        request,
        "jobseeker_register.html"
    )

def recruiter_register(request):
    print("RECRUITER VIEW HIT")
    print(request.method)
    if request.method == "POST":

        recruiter_name = request.POST.get("recruiter_name")
        company_name = request.POST.get("company_name")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if not recruiter_name or not company_name or not email or not password1:

            return render(
                request,
                "recruiter_register.html",
                {"error": "All fields are required"}
            )

        if password1 != password2:
            return render(
                request,
                "recruiter_register.html",
                {"error": "Passwords do not match"}
            )

        if User.objects.filter(email=email).exists():
            return render(
                request,
                "recruiter_register.html",
                {"error": "Email already exists"}
            )

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=recruiter_name
        )

        UserRole.objects.create(
            user=user,
            role="recruiter"
        )

        RecruiterProfile.objects.create(
            user=user,
            recruiter_name=recruiter_name,
            company_name=company_name,
            company_email=email
        )

        login(request, user)
        print("Recruiter created")
        print("Redirecting to dashboard")

        return redirect("recruiter_profile_setup")

    return render(
        request,
        "recruiter_register.html"
    )


def jobseeker_login(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:

            login(request, user)

            role = UserRole.objects.get(user=user)

            if role.role == "recruiter":
                return redirect("recruiter_dashboard")

            elif role.role == "jobseeker":
                return redirect("jobseeker_dashboard")
            
        return render(
            request,
            "login.html",
            {"error": "Invalid email or password"}
        )

    return render(request, "login.html")


@login_required
def jobseeker_profile_setup(request):

    profile = JobSeekerProfile.objects.filter(user=request.user).first()


    if request.method == "POST":

        JobSeekerProfile.objects.update_or_create(

            user=request.user,

            defaults={

               "phone":request.POST.get("phone"),

               "country":request.POST.get("country"),

               "state":request.POST.get("state"),

               "city":request.POST.get("city"),

               "education":request.POST.get("education"),

               "field":request.POST.get("field"),

               "preferred_job_role":request.POST.get(
                "preferred_job_role"
               ),

               "experience_level":request.POST.get(
                "experience_level"
               ),

              "skills":request.POST.get("skills"),

              "linkedin":request.POST.get("linkedin"),

              "resume":request.FILES.get("resume"),

              "profile_completed":True

            }
        )

        return redirect("jobseeker_dashboard")

    return render(
        request,
        "jobseeker_profile_setup.html",
        {"profile": profile}
    )


@login_required
def recruiter_profile_setup(request):

    recruiter = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

    if request.method == "POST":

        # recruiter.recruiter_name = request.POST.get("recruiter_name")

        # recruiter.company_name = request.POST.get("company_name")

        # recruiter.company_email = request.POST.get("company_email")

        recruiter.company_phone = request.POST.get("company_phone")


        recruiter.company_website = request.POST.get("company_website")

        recruiter.industry = request.POST.get("industry")

        recruiter.company_location = request.POST.get("company_location")

        recruiter.company_description = request.POST.get("company_description")

        recruiter.total_employees = request.POST.get("total_employees") or 1

        recruiter.founded_year = request.POST.get("founded_year")

        recruiter.company_rating = request.POST.get("company_rating") or 5.0

        

        if request.FILES.get("company_logo"):

            recruiter.company_logo = request.FILES.get(
                "company_logo"
            )

        recruiter.profile_completed = True

        recruiter.save()

        messages.success(
            request,
            "Profile updated successfully."
        )
        return redirect(
            "recruiter_profile"
        )

    context = {

        "recruiter": recruiter

    }

    return render(
        request,
        "recruiter/profile_setup.html",
        context,
    )



@login_required
def jobseeker_profile(request):
    user = request.user
    profile = JobSeekerProfile.objects.filter(user=user).first()

    if profile:
        completeness = profile.completeness_percent()
        skills_list = [s.strip() for s in profile.skills.split(",") if s.strip()]
    else:
        completeness = 0
        skills_list = []

    circumference = 138.2
    ring_offset = round(circumference - (completeness / 100 * circumference), 1)

    full_name = user.first_name or user.email
    initials = "".join([p[0].upper() for p in full_name.split()[:2]]) if full_name else "U"

    context = {
        "full_name": full_name,
        "email": user.email,
        "initials": initials,
        "profile": profile,
        "skills_list": skills_list,
        "completeness": completeness,
        "ring_offset": ring_offset,
    }
    return render(request, "jobseeker/profile.html", context)


@login_required
def jobseeker_dashboard(request):

    role = UserRole.objects.get(user=request.user)

    if role.role != "jobseeker":
        return redirect("recruiter_dashboard")

    user = request.user

    applications = Application.objects.filter(user=user)

    applied_count = applications.count()
    shortlisted_count = applications.filter(
        status="Shortlisted"
    ).count()

    interviewing_count = applications.filter(
        status="Interviewing"
    ).count()

    rejected_count = applications.filter(
        status="Rejected"
    ).count()

    recent_applications = applications[:3]
    applied_job_ids = list(
    applications.values_list(
        "job_id",
        flat=True
    )
    )

    try:
        profile = JobSeekerProfile.objects.get(user=user)

        completeness = profile.completeness_percent()

        user_skills = {
            skill.strip().lower()
            for skill in profile.skills.split(",")
            if skill.strip()
        }

        jobs = Job.objects.filter(
            is_published=True,
            is_closed=False
        )

        recommended_jobs = []

        for job in jobs:

            job_skills = {
                skill.strip().lower()
                for skill in job.skills.split(",")
                if skill.strip()
            }

            # Skill Match %
            if job_skills:
                skill_match = (
                    len(user_skills.intersection(job_skills))
                    / len(job_skills)
                ) * 100
            else:
                skill_match = 0

            # Role Match Bonus
            role_match = (
                profile.preferred_job_role.lower()
                in job.title.lower()
            )

            final_match = skill_match

            if role_match:
                final_match += 25

            final_match = min(round(final_match), 100)

            if final_match > 0:
                recommended_jobs.append({
                    "job": job,
                    "match": final_match
                })

        recommended_jobs = sorted(
            recommended_jobs,
            key=lambda x: x["match"],
            reverse=True
        )[:3]

    except JobSeekerProfile.DoesNotExist:

        logout(request)
        messages.error(
            request,
            "Your account has been deleted .Please contact the administrator."

        )
        return redirect("login")   

    circumference = 138.2

    ring_offset = round(
        circumference - (completeness / 100 * circumference),
        1
    )

    full_name = user.first_name or user.email

    name_parts = full_name.split()

    initials = "".join(
        [p[0].upper() for p in name_parts[:2]]
    ) if name_parts else "U"

    context = {
        "full_name": full_name,
        "email": user.email,
        "initials": initials,
        "applied_count": applied_count,
        "shortlisted_count": shortlisted_count,
        "interviewing_count": interviewing_count,
        "rejected_count": rejected_count,
        "recent_applications": recent_applications,
        "recommended_jobs": recommended_jobs,
        "applied_job_ids": applied_job_ids,
        "completeness": completeness,
        "ring_offset": ring_offset,
    }

    return render(
        request,
        "jobseeker/dashboard.html",
        context
    )

@login_required
def recruiter_dashboard(request):

    role = UserRole.objects.get(user=request.user)

    if role.role != "recruiter":
        return redirect("jobseeker_dashboard")

    recruiter = RecruiterProfile.objects.get(
        user=request.user
    )

    all_jobs = Job.objects.filter(
        recruiter=recruiter
    )

    recent_jobs = all_jobs.order_by("-created_at")[:5]

    active_jobs = sum(
        1 for job in all_jobs
        if job.status in ["Active", "Closing Soon"]
    )

    context = {
        "active_jobs": active_jobs,
        "recent_jobs": recent_jobs,
    }

    return render(
        request,
        "recruiter/dashboard.html",
        context
    )

@login_required
def job_tracker(request):

    applications = Application.objects.filter(
        user=request.user
    ).select_related(
        "job",
        "job__recruiter"
    )

    # Search
    search_query = request.GET.get("q", "").strip()

    if search_query:
        applications = applications.filter(
            Q(job__title__icontains=search_query) |
            Q(
                job__recruiter__company_name__icontains=
                search_query
            )
        )

    # Status Filter
    status_filter = request.GET.get("status", "")

    if status_filter:
        applications = applications.filter(
            status=status_filter
        )

    # Sorting
    sort_by = request.GET.get("sort", "newest")

    if sort_by == "oldest":

        applications = applications.order_by(
            "applied_date"
        )

    elif sort_by == "company":

        applications = applications.order_by(
            "job__recruiter__company_name"
        )

    else:

        applications = applications.order_by(
            "-applied_date"
        )

    # Pipeline Stats
    all_applications = Application.objects.filter(
        user=request.user
    )

    total_count = all_applications.count()

    status_counts = {
    "Applied": all_applications.filter(
        status__in=[
            "Applied",
            "Viewed",
            "Shortlisted",
            "Interviewing",
            "Offer",
            "Rejected",
        ]
    ).count(),

    "Shortlisted": all_applications.filter(
        status__in=[
            "Shortlisted",
            "Interviewing",
            "Offer",
            "Rejected",
        ]
    ).count(),

    "Interviewing": all_applications.filter(
        status__in=[
            "Interviewing",
            "Offer",
            "Rejected",
        ]
    ).count(),

    "Offer": all_applications.filter(
        status__in=[
            "Offer",
            "Rejected",
        ]
    ).count(),

    "Rejected": all_applications.filter(
        status="Rejected"
    ).count(),
}

    def pct(count):

        return round(
            (count / total_count) * 100
        ) if total_count else 0

    status_percents = {
        key: pct(value)
        for key, value in status_counts.items()
    }

    context = {

        "applications": applications,

        "total_count": total_count,

        "status_counts": status_counts,

        "status_percents": status_percents,

        "search_query": search_query,

        "status_filter": status_filter,

        "sort_by": sort_by,

        "status_choices": Application.STATUS_CHOICES,
    }

    return render(
        request,
        "jobseeker/job_tracker.html",
        context
    )

 
 
@login_required
def update_application_jsstatus(request, application_id):
    application = get_object_or_404(Application, id=application_id)
 

    if request.method == "POST":
        new_status = request.POST.get("status")
        valid_statuses = dict(Application.STATUS_CHOICES)
        if new_status in valid_statuses:
            application.status = new_status
            application.save()
            messages.success(request, "Application status updated.")
    return redirect("job_tracker")



# def add_job(request):


#     if request.method == "POST":

#         company_name = request.POST.get("company")
#         title = request.POST.get("title")
#         location = request.POST.get("location")
#         description = request.POST.get("description")

#         company, created = Company.objects.get_or_create(
#             name=company_name
#         )

#         Job.objects.create(
#             company=company,
#             title=title,
#             location=location,
#             description=description
#         )

#         return redirect("job_list")

#     return render(request, "recruiter/add_job.html")

@login_required
def apply_job(request, job_id):

    job = Job.objects.get(id=job_id)

    already_applied = Application.objects.filter(
        user=request.user,
        job=job
    ).exists()

    if not already_applied:

        profile = JobSeekerProfile.objects.get(
            user=request.user
        )

        job_skills = {
            skill.strip().lower()
            for skill in job.skills.split(",")
            if skill.strip()
        }

        candidate_skills = {
            skill.strip().lower()
            for skill in profile.skills.split(",")
            if skill.strip()
        }

        matched_skills = job_skills.intersection(
            candidate_skills
        )

        # Base score
        if job_skills:
            match_score = round(
                (len(matched_skills) / len(job_skills)) * 100
            )
        else:
            match_score = 0

        # Role bonus
        if profile.preferred_job_role.lower() in job.title.lower():
            match_score += 20

        match_score = min(match_score, 100)

        Application.objects.create(
            user=request.user,
            job=job,
            status="Applied",
            match_score=match_score,
            matched_skills=", ".join(
                sorted(matched_skills)[:5]
            )
        )

        Notification.objects.create(
            recipient=job.recruiter.user,
            message=f"{request.user.first_name or request.user.email} applied for {job.title}",
            link=reverse("manage_applications")
        )

    return redirect("jobseeker_dashboard")

@login_required
def job_list(request):
    jobs = Job.objects.filter(
        is_published=True,
        is_closed=False
    )


    search_query = request.GET.get("q", "").strip()

    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(skills__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(recruiter__company_name__icontains=search_query)
        )

    applied_job_ids = list(
        Application.objects.filter(
            user=request.user
        ).values_list("job_id", flat=True)
    )

    context = {
        "jobs": jobs,
        "search_query": search_query,
        "applied_job_ids": applied_job_ids,
    }


    return render(request,"jobseeker/job_list.html",{"jobs": jobs}
)

@login_required
def ats_resume(request):
    return render(request, "jobseeker/ats_resume.html")

@login_required
def email_generator(request):
    return render(request, "jobseeker/email_generator.html")

@login_required
def cover_letter(request):
    return render(request, "jobseeker/cover_letter.html")

@login_required
def interview_prep(request):
    return render(request, "jobseeker/interview_prep.html")

# @login_required
# def jobseeker_logout(request):
#     logout(request)
#     return redirect("jobseeker_login")

def logout_view(request):
    logout(request)

    return redirect("/")

@login_required
def jobseeker_settings(request):
    user = request.user
    profile = JobSeekerProfile.objects.filter(user=user).first()

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "account_info":
            fullname = request.POST.get("full_name")
            user.first_name = fullname
            user.email = request.POST.get("email")
            user.save()

            JobSeekerProfile.objects.update_or_create(
                user=user,
                defaults={"phone": request.POST.get("phone")}
            )
            messages.success(request, "Account info updated.")

        elif form_type == "change_password":
            current_pw = request.POST.get("current_password")
            new_pw = request.POST.get("new_password")
            confirm_pw = request.POST.get("confirm_password")

            if not user.check_password(current_pw):
                messages.error(request, "Current password is incorrect.")
            elif new_pw != confirm_pw:
                messages.error(request, "New passwords do not match.")
            elif len(new_pw) < 8:
                messages.error(request, "New password must be at least 8 characters.")
            else:
                user.set_password(new_pw)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated.")

        elif form_type == "notifications":
            if profile:
                profile.notify_job_recs = "notify_job_recs" in request.POST
                profile.notify_app_updates = "notify_app_updates" in request.POST
                profile.save()
                messages.success(request, "Notification preferences saved.")

        elif form_type == "privacy":
            if profile:
                profile.profile_visible = "profile_visible" in request.POST
                profile.save()
                messages.success(request, "Privacy settings saved.")

        elif form_type == "delete_account":
            logout(request)
            user.delete()
            messages.success(request, "Your account has been deleted.")
            return redirect("jobseeker_login")

        return redirect("jobseeker_settings")

    context = {
        "profile": profile,
        "full_name": user.first_name or user.email,
        "email": user.email,
    }
    return render(request, "jobseeker/settings.html", context)

    return redirect("home")


@login_required
def recruiter_profile(request):
     
    recruiter = get_object_or_404(
        RecruiterProfile,
        user=request.user
    )

    context = {
        "recruiter": recruiter
    }

    return render(
        request,
        "recruiter/recruiter_profile.html",
        context
    )
    


@login_required
def recruiter_settings(request):

    recruiter = RecruiterProfile.objects.get(
        user=request.user
    )

    if request.method == "POST":

        recruiter.candidate_agent_enabled = (
            "candidate_agent_enabled"
            in request.POST
        )

        recruiter.save()

        messages.success(
            request,
            "Settings updated successfully."
        )

        return redirect(
            "recruiter_settings"
        )

    return render(
        request,
        "recruiter/recruiter_settings.html",
        {
            "recruiter": recruiter
        }
    )

@login_required
def post_job(request):

    recruiter = RecruiterProfile.objects.get(
        user=request.user
    )

    if request.method == "POST":

        job = Job.objects.create(

            recruiter=recruiter,

            title=request.POST.get("title"),

            location=request.POST.get("location"),

            employment_type=request.POST.get(
                "employment_type"
            ),

            salary=request.POST.get("salary"),

            valid_until=request.POST.get("valid_until"),

            skills=request.POST.get("skills"),

            description=request.POST.get(
                "description"
            )
        )

        return redirect("job_postings")

    return render(
        request,
        "recruiter/post_job.html"
    )

@login_required
def job_postings(request):

    recruiter = RecruiterProfile.objects.get(
        user=request.user
    )

    status_filter = request.GET.get("status")
    search_query = request.GET.get("q", "").strip()

    all_jobs = Job.objects.filter(
        recruiter=recruiter
    )

    # Counts
    all_count = all_jobs.count()

    active_count = sum(1 for job in all_jobs if job.status == "Active")
    closing_count = sum(1 for job in all_jobs if job.status == "Closing Soon")
    draft_count = sum(1 for job in all_jobs if job.status == "Draft")
    closed_count = sum(1 for job in all_jobs if job.status == "Closed")

    jobs_qs = all_jobs

    if search_query:
        jobs_qs = jobs_qs.filter(
            Q(title__icontains=search_query) | Q(skills__icontains=search_query)
        )

    if status_filter:
        jobs = [job for job in jobs_qs if job.status == status_filter]
    else:
        jobs = list(jobs_qs)

    return render(
        request,
        "recruiter/job_postings.html",
        {
            "jobs": jobs,
            "all_count": all_count,
            "active_count": active_count,
            "closing_count": closing_count,
            "draft_count": draft_count,
            "closed_count": closed_count,
            "current_status": status_filter,
            "search_query": search_query,
        }
    )

@login_required
def publish_job(request, job_id):

    job = Job.objects.get(id=job_id)

    job.is_published = True
    job.save()

    run_candidate_graph(
        job.id
    )

    return redirect("job_postings")


@login_required
def close_job(request, job_id):

    job = Job.objects.get(id=job_id)

    job.is_closed = True
    job.is_reposted = False

    job.save()

    return redirect("job_postings")


@login_required
def repost_job(request, job_id):

    job = Job.objects.get(id=job_id)

    if request.method == "POST":

        # print("REPOST CLICKED")
        job.valid_until = request.POST.get("valid_until")
        job.is_closed = False
        job.is_published = True

        job.reposted_at = timezone.now()

        job.save()

        return redirect("job_postings")

    return render(
        request,
        "recruiter/repost_job.html",
        {"job": job}
    )

@login_required
def view_job(request, job_id):

    job = Job.objects.get(id=job_id)

    return render(
        request,
        "recruiter/view.html",
        {"job": job}
    )

def manage_jobs(request):

    recruiter = RecruiterProfile.objects.get(user=request.user)

    jobs = Job.objects.filter(
        recruiter=recruiter
    ).order_by("-created_at")

    context = {
        "jobs": jobs
    }

    return render(
        request,
        "recruiter/manage_jobs.html",
        context
    )
@login_required
def edit_job(request, job_id):
    recruiter_profile = get_object_or_404(RecruiterProfile, user=request.user)
    job = get_object_or_404(Job, id=job_id, recruiter=recruiter_profile) 

    if request.method == "POST":
        job.title = request.POST.get('title')
        job.location = request.POST.get('location')
        job.employment_type = request.POST.get('employment_type') or job.employment_type
        job.salary = request.POST.get('salary')
        job.skills = request.POST.get('skills', job.skills)
        job.description = request.POST.get('description')
        job.valid_until = request.POST.get('valid_until') or job.valid_until
        
        job.save()
        messages.success(request, "Job updated successfully.")
        return redirect('manage_jobs')
       
        
    return render(request, 'recruiter/edit_job.html', {'job': job})

@login_required
@require_POST
def delete_job(request, job_id):
    recruiter_profile = get_object_or_404(RecruiterProfile, user=request.user)
    job = get_object_or_404(Job, id=job_id, recruiter=recruiter_profile)
    job.delete()
    messages.success(request, "Job deleted successfully.")
    return redirect('manage_jobs')

@login_required
def candidates_list(request):

    recruiter = RecruiterProfile.objects.get(user=request.user)

    skill_query = request.GET.get("skill", "").strip()
    experience_filter = request.GET.get("experience", "")
    location_query = request.GET.get("location", "").strip()

    candidates = JobSeekerProfile.objects.filter(
        profile_completed=True
    )

    if skill_query:
        candidates = candidates.filter(
            Q(skills__icontains=skill_query) |
            Q(preferred_job_role__icontains=skill_query) |
            Q(user__first_name__icontains=skill_query)
        )

    if experience_filter:
        candidates = candidates.filter(
            experience_level=experience_filter
        )

    if location_query:
        candidates = candidates.filter(
            Q(city__icontains=location_query) |
            Q(state__icontains=location_query) |
            Q(country__icontains=location_query)
        )

    candidates = candidates.order_by("-created_at")

    # jobs this recruiter can invite candidates for
    recruiter_jobs = Job.objects.filter(
        recruiter=recruiter,
        is_published=True,
        is_closed=False
    )

    # candidates already invited by this recruiter
    invited_user_ids = Invitation.objects.filter(
        recruiter=recruiter
    ).values_list("candidate_id", flat=True)

    context = {
        "candidates": candidates,
        "recruiter_jobs": recruiter_jobs,
        "invited_user_ids": list(invited_user_ids),
        "skill_query": skill_query,
        "experience_filter": experience_filter,
        "location_query": location_query,
        "experience_choices": JobSeekerProfile.EXPERIENCE_CHOICES,
    }

    return render(
        request,
        "recruiter/candidates.html",
        context
    )


@login_required
def candidate_profile_view(request, candidate_id):

    candidate = get_object_or_404(
        JobSeekerProfile,
        id=candidate_id
    )

    skills_list = [
        s.strip() for s in candidate.skills.split(",") if s.strip()
    ]

    recruiter = RecruiterProfile.objects.get(user=request.user)

    recruiter_jobs = Job.objects.filter(
        recruiter=recruiter,
        is_published=True,
        is_closed=False
    )

    already_invited = Invitation.objects.filter(
        recruiter=recruiter,
        candidate=candidate.user
    ).exists()

    context = {
        "candidate": candidate,
        "skills_list": skills_list,
        "recruiter_jobs": recruiter_jobs,
        "already_invited": already_invited,
    }

    return render(
        request,
        "recruiter/candidate_profile.html",
        context
    )


@login_required
def invite_candidate(request, candidate_id):

    if request.method == "POST":

        recruiter = RecruiterProfile.objects.get(user=request.user)

        candidate = get_object_or_404(
            JobSeekerProfile,
            id=candidate_id
        )

        job_id = request.POST.get("job_id")

        job = None

        if job_id:
            job = Job.objects.filter(
                id=job_id,
                recruiter=recruiter
            ).first()

        already_invited = Invitation.objects.filter(
            recruiter=recruiter,
            candidate=candidate.user
        ).exists()

        if not already_invited:

            Invitation.objects.create(
                recruiter=recruiter,
                candidate=candidate.user,
                job=job
            )

    return redirect(request.META.get("HTTP_REFERER", "candidates"))

def notifications(request):

    if not request.user.is_authenticated:
        return {}

    items = []

    invitations = Invitation.objects.filter(
        candidate=request.user
    ).order_by("-created_at")[:10]

    for inv in invitations:
        items.append({
            "message": f"{inv.recruiter.company_name} invited you"
                       + (f" to apply for {inv.job.title}" if inv.job else ""),
            "link": reverse("mark_notification_read", args=[inv.id]),
            "is_read": inv.is_read,
            "created_at": inv.created_at,
        })

    general = Notification.objects.filter(
        recipient=request.user
    ).order_by("-created_at")[:10]

    for n in general:
        items.append({
            "message": n.message,
            "link": reverse("mark_general_notification_read", args=[n.id]),
            "is_read": n.is_read,
            "created_at": n.created_at,
        })

    items.sort(key=lambda x: x["created_at"], reverse=True)
    items = items[:10]

    unread_count = (
        Invitation.objects.filter(
            candidate=request.user,
            is_read=False
        ).count()
        +
        Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
    )

    return {
        "topnav_notifications": items,
        "unread_notifications_count": unread_count,
    }

@login_required
def mark_notification_read(request, invitation_id):

    invitation = get_object_or_404(
        Invitation,
        id=invitation_id,
        candidate=request.user
    )

    invitation.is_read = True
    invitation.save()
    
    if invitation.job:
        return redirect("job_detail", job_id=invitation.job.id)

    return redirect(request.META.get("HTTP_REFERER", "jobseeker_dashboard"))

@login_required
def mark_general_notification_read(request, notification_id):

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )

    notification.is_read = True
    notification.save()

    if notification.link:
        return redirect(notification.link)

    return redirect(request.META.get("HTTP_REFERER", "/"))

@login_required
def job_detail(request, job_id):

    job = get_object_or_404(Job, id=job_id)

    already_applied = Application.objects.filter(
        user=request.user,
        job=job
    ).exists()

    context = {
        "job": job,
        "already_applied": already_applied,
        "can_apply": job.is_published and not job.is_closed,
    }

    return render(request, "jobseeker/job_detail.html", context)

@login_required
def manage_applications(request, job_id=None):
    recruiter = get_object_or_404(RecruiterProfile, user=request.user)
    
    if job_id:
        job = get_object_or_404(Job, id=job_id, recruiter=recruiter)
        applications = Application.objects.filter(job=job).select_related('user', 'job').order_by('-applied_date')
    else:
        jobs = Job.objects.filter(recruiter=recruiter)
        applications = Application.objects.filter(job__in=jobs).select_related('user', 'job').order_by('-applied_date')         
        search_query = request.GET.get('q', '').strip()

    search_query = request.GET.get('q', '').strip()
    if search_query:
        applications = applications.filter(job__title__icontains=search_query)

    status_counts = {
    'Viewed': applications.filter(
        status__in=['Viewed', 'Shortlisted', 'Interviewing', 'Rejected']
    ).count(),

    'Shortlisted': applications.filter(
        status__in=['Shortlisted', 'Interviewing', 'Rejected']
    ).count(),

    'Interviewing': applications.filter(
        status__in=['Interviewing', 'Rejected']
    ).count(),

    'Rejected': applications.filter(
        status='Rejected'
    ).count(),
}
    
    context = {
        'applications': applications,
        'selected_job': job_id,
        'search_query': search_query,
        'jobs': Job.objects.filter(recruiter=recruiter, is_published=True),
        'status_counts': status_counts,
        'status_choices': Application.STATUS_CHOICES,

    }
    return render(request, 'recruiter/manage_applications.html', context)


@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id, job__recruiter__user=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        valid_statuses = dict(Application.STATUS_CHOICES)
        if new_status in valid_statuses:
            application.status = new_status
            
            if new_status != 'Rejected':
                application.rejection_reason = ''
            
            application.save()

            status_messages = {
                "Viewed": f"Your application for {application.job.title} was viewed",
                "Shortlisted": f"You've been shortlisted for {application.job.title}",
                "Interviewing": f"You're moving to interview stage for {application.job.title}",
                "Rejected": f"Your application for {application.job.title} was not selected",
            }

            Notification.objects.create(
            recipient=application.user,
            message=status_messages.get(
                new_status,
                f"Your application status updated to {new_status}"
            ),
            link=reverse("job_tracker")
        )


            
            messages.success(request, f"Application status updated to {new_status}.")
            
            
            if new_status == 'Rejected':
                return redirect('add_rejection_reason', application_id=application_id)
            
            return redirect('manage_applications')
        else:
            messages.error(request, "Invalid status selected.")
            return redirect('manage_applications')
    
    context = {
        'application': application,
        'status_choices': Application.STATUS_CHOICES,
    }
    return render(request, 'recruiter/update_status.html', context)

@login_required
def add_rejection_reason(request, application_id):
    application = get_object_or_404(Application, id=application_id, job__recruiter__user=request.user)
    
    if application.status != 'Rejected':
        messages.error(request, "Only rejected applications can have a reason added.")
        return redirect('manage_applications')
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '').strip()
        application.rejection_reason = rejection_reason if rejection_reason else None
        application.save()
        
        if rejection_reason:
            messages.success(request, "Rejection reason added successfully.")
        else:
            messages.info(request, "Application rejected without a reason.")
        
        return redirect('manage_applications')
    
    context = {
        'application': application,
    }
    return render(request, 'recruiter/add_rejection_reason.html', context)

@login_required
def clear_notifications(request):

    Notification.objects.filter(
        recipient=request.user
    ).delete()

    return redirect(request.META.get(
        "HTTP_REFERER",
        "recruiter_dashboard"
    ))

@login_required
def clear_notificationsjs(request):

    Notification.objects.filter(
        recipient=request.user
    ).delete()

    Invitation.objects.filter(
        candidate=request.user
    ).delete()

    return redirect(
        request.META.get(
            "HTTP_REFERER",
            "jobseeker_dashboard"
        )
    )