from django.shortcuts import render,redirect,get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login,logout
from .models import JobSeekerProfile
from .models import JobSeekerProfile, Job, Application,Company
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash


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

        # Automatically log user in
        login(request, user)

        # Send them to profile setup
        return redirect("jobseeker_profile_setup")

    return render(
        request,
        "jobseeker_register.html"
    )

def recruiter_register(request):
    return render(request, 'recruiter_register.html')

from django.contrib.auth import authenticate

def jobseeker_login(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
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
    user = request.user
 
    # Real applications for the logged-in user only
    applications = Application.objects.filter(user=user)
 
    applied_count = applications.count()
    shortlisted_count = applications.filter(status="Shortlisted").count()
    interviewing_count = applications.filter(status="Interviewing").count()
    rejected_count = applications.filter(status="Rejected").count()
 
    recent_applications = applications[:3]  # already ordered by -applied_date
 
    recommended_jobs = Job.objects.filter(is_active=True).order_by("-posted_date")[:3]
 
    # Profile completeness — pulls from the profile this user filled during setup
    try:
        profile = JobSeekerProfile.objects.get(user=user)
        completeness = profile.completeness_percent()
    except JobSeekerProfile.DoesNotExist:
        completeness = 0
 
    circumference = 138.2
    ring_offset = round(circumference - (completeness / 100 * circumference), 1)
 
    full_name = user.first_name or user.email
    name_parts = full_name.split()
    initials = "".join([p[0].upper() for p in name_parts[:2]]) if name_parts else "U"
 
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
        "completeness": completeness,
        "ring_offset": ring_offset,
    }
    return render(request, "jobseeker/dashboard.html", context)

@login_required
def job_tracker(request):
    applications = Application.objects.filter(
        user=request.user
    ).select_related("job", "job__company")
 
    # ---- Search ----
    search_query = request.GET.get("q", "").strip()
    if search_query:
        applications = applications.filter(
            Q(job__title__icontains=search_query) |
            Q(job__company__name__icontains=search_query)
        )
 
    # ---- Filter by status ----
    status_filter = request.GET.get("status", "")
    if status_filter:
        applications = applications.filter(status=status_filter)
 
    # ---- Sort ----
    sort_by = request.GET.get("sort", "newest")
    if sort_by == "oldest":
        applications = applications.order_by("applied_date")
    elif sort_by == "company":
        applications = applications.order_by("job__company__name")
    else:
        applications = applications.order_by("-applied_date")
 
    # ---- Pipeline stats (for the funnel summary) ----
    all_applications = Application.objects.filter(user=request.user)
    total_count = all_applications.count()
 
    status_counts = {
        "Applied": all_applications.filter(status="Applied").count(),
        "Shortlisted": all_applications.filter(status="Shortlisted").count(),
        "Interviewing": all_applications.filter(status="Interviewing").count(),
        "Offer": all_applications.filter(status="Offer").count(),
        "Rejected": all_applications.filter(status="Rejected").count(),
    }
 
    def pct(count):
        return round((count / total_count) * 100) if total_count else 0
 
    status_percents = {key: pct(value) for key, value in status_counts.items()}
 
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
    return render(request, "jobseeker/job_tracker.html")

 
 
@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id)
 
    if request.method == "POST":
        new_status = request.POST.get("status")
        valid_statuses = dict(Application.STATUS_CHOICES)
        if new_status in valid_statuses:
            application.status = new_status
            application.save()
            messages.success(request, "Application status updated.")
    return redirect("job_tracker")


def add_job(request):

    if request.method == "POST":

        company_name = request.POST.get("company")
        title = request.POST.get("title")
        location = request.POST.get("location")
        description = request.POST.get("description")

        company, created = Company.objects.get_or_create(
            name=company_name
        )

        Job.objects.create(
            company=company,
            title=title,
            location=location,
            description=description
        )

        return redirect("job_list")

    return render(request, "recruiter/add_job.html")

@login_required
def apply_job(request, job_id):

    job = Job.objects.get(id=job_id)

    Application.objects.create(
        user=request.user,
        job=job,
        status="Applied"
    )

    return redirect("jobseeker_dashboard")

@login_required
def job_list(request):
    jobs = Job.objects.filter(is_active=True)

    return render(
        request,
        "jobseeker/job_list.html",
        {"jobs": jobs}
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

@login_required
def jobseeker_logout(request):
    logout(request)
    return redirect("jobseeker_login")

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