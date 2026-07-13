from django.urls import path
from . import views

app_name = "ghost_hunter"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
]