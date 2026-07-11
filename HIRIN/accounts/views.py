from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login,logout
from .models import JobSeekerProfile, RecruiterProfile, UserRole, Job, Application
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.utils import timezone

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

    recruiter = RecruiterProfile.objects.get(
        user=request.user
    )

    if request.method == "POST":

        recruiter.company_website = request.POST.get(
            "company_website"
        )

        recruiter.industry = request.POST.get(
            "industry"
        )

        recruiter.company_location = request.POST.get(
            "company_location"
        )

        recruiter.company_phone = request.POST.get(
            "company_phone"
        )

        recruiter.company_description = request.POST.get(
            "company_description"
        )

        if request.FILES.get("company_logo"):

            recruiter.company_logo = request.FILES.get(
                "company_logo"
            )

        recruiter.profile_completed = True

        recruiter.save()

        return redirect(
            "recruiter_dashboard"
        )

    return render(
        request,
        "recruiter/profile_setup.html",
        {
            "recruiter": recruiter
        }
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
 
    recommended_jobs = Job.objects.filter(
    is_published=True,
    is_closed=False
    ).order_by("-created_at")[:3]
 
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
def recruiter_dashboard(request):

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
    return render(request, "jobseeker/job_tracker.html")

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

    Application.objects.create(
        user=request.user,
        job=job,
        status="Applied"
    )

    return redirect("jobseeker_dashboard")

@login_required
def job_list(request):
    jobs = Job.objects.filter(
        is_published=True,
        is_closed=False
    )

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

# @login_required
# def jobseeker_logout(request):
#     logout(request)
#     return redirect("jobseeker_login")

def logout_view(request):
    logout(request)
    return redirect("home")

@login_required
def post_job(request):

    recruiter = RecruiterProfile.objects.get(
        user=request.user
    )

    if request.method == "POST":

        Job.objects.create(

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

    all_jobs = Job.objects.filter(
        recruiter=recruiter
    )

    # Counts
    all_count = all_jobs.count()

    active_count = 0
    closing_count = 0
    draft_count = 0
    closed_count = 0

    for job in all_jobs:

        if job.status == "Active":
            active_count += 1

        elif job.status == "Closing Soon":
            closing_count += 1

        elif job.status == "Draft":
            draft_count += 1

        elif job.status == "Closed":
            closed_count += 1

    # Filtering
    if status_filter:

        jobs = []

        for job in all_jobs:

            if job.status == status_filter:
                jobs.append(job)

    else:

        jobs = all_jobs

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
        }
    )

@login_required
def publish_job(request, job_id):

    job = Job.objects.get(id=job_id)

    job.is_published = True
    job.save()

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