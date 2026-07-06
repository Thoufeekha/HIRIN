from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import JobSeekerProfile


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
        return redirect("/jobseeker_profile_setup/")

    return render(
        request,
        "jobseeker_register.html"
    )

def recruiter_register(request):
    return render(request, 'recruiter_register.html')

from django.contrib.auth.decorators import login_required

@login_required
def jobseeker_profile_setup(request):

    if request.method == "POST":

        JobSeekerProfile.objects.create(

            user=request.user,

            phone=request.POST.get("phone"),

            country=request.POST.get("country"),

            state=request.POST.get("state"),

            city=request.POST.get("city"),

            education=request.POST.get("education"),

            field=request.POST.get("field"),

            preferred_job_role=request.POST.get(
                "preferred_job_role"
            ),

            experience_level=request.POST.get(
                "experience_level"
            ),

            skills=request.POST.get("skills"),

            linkedin=request.POST.get("linkedin"),

            resume=request.FILES.get("resume"),

            profile_completed=True
        )

        return redirect("/")

    return render(
        request,
        "jobseeker_profile_setup.html"
    )