from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def index(request):
    return render(request, 'index.html')

def companies(request):
    return render(request, 'companies.html')

# def service(request):
#     return render(request, 'companies.html')


def FAQ(request):
    return render(request, 'FAQ.html')

def login(request):
    return render(request, 'login.html')

# def signup(request):
#     return render(request, 'signup.html')

def getstarted(request):
    return render(request, 'getstarted.html')