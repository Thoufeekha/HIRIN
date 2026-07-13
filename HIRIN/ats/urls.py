from django.urls import path
from . import views

urlpatterns = [
    path("", views.ats_resume, name="ats_resume"),
]