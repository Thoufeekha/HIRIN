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
    return render(request, 'FAQ.html')

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

            return redirect("/")

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