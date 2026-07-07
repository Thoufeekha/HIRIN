from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
# Create your views here.
def index(request):
    return render(request, 'index.html')

def companies(request):
    return render(request, 'companies.html')

# def service(request):
#     return render(request, 'companies.html')


def FAQ(request):
    jobseeker_faqs = [
        {"question": "How do I create an account?",
         "answer": "Click Get Started on the homepage, choose Job Seeker, and fill in your basic details along with email verification."},
        {"question": "How can I search for jobs?",
         "answer": "Use the search bar on the Companies page to filter jobs by role, location, or required skills."},
        {"question": "How do I apply for a job?",
         "answer": "Open any job listing and click Apply Now. Your profile and resume will be sent to the recruiter automatically."},
        {"question": "How can I track my application status?",
         "answer": "Go to My Applications in your dashboard to see real-time status updates for each job you applied to."},
        {"question": "Can I edit or update my profile?",
         "answer": "Yes, go to Account Settings anytime to update your resume, skills, or personal details."},
        {"question": "Is my personal information safe?",
         "answer": "Yes, your resume and contact details are only visible to recruiters you apply to, and are never shared with third parties."},
    ]

    recruiter_faqs = [
        {"question": "How do I post a new job?",
         "answer": "From your Recruiter dashboard, click Post a Job, fill in the role details and requirements, then publish."},
        {"question": "Can I edit or delete a job post?",
         "answer": "Yes, open the listing under My Postings and choose Edit or Delete."},
        {"question": "How does candidate matching work?",
         "answer": "Our AI parses your job description into key skills and experience criteria, then scores each applicant's resume against them automatically."},
        {"question": "Can I filter candidates by ATS score?",
         "answer": "Yes, the candidate list under each job posting can be sorted by ATS match score, highest first."},
        {"question": "Can I contact candidates directly?",
         "answer": "Yes, use the AI Email Generator from the candidate's profile to draft and send an interview invitation."},
        {"question": "Is candidate data shared with third parties?",
         "answer": "No, candidate resumes and contact details are only visible to your recruiter account."},
    ]

    return render(request, 'FAQ.html', {
        'jobseeker_faqs': jobseeker_faqs,
        'recruiter_faqs': recruiter_faqs,
        })

def login_view(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,   # username=email because you saved it that way
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect("jobseeker_dashboard")

        return render(
            request,
            "login.html",
            {"error": "Invalid email or password"}
        )

    return render(request, "login.html")

# def signup(request):
#     return render(request, 'signup.html')

def getstarted(request):
    return render(request, 'getstarted.html')