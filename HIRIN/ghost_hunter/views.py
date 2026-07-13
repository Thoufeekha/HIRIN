from django.http import HttpResponse

def dashboard(request):
    return HttpResponse("Ghost Hunter is working!")