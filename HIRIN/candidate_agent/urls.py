from django.urls import path
from . import views

urlpatterns = [

    path(
        "invites/<int:job_id>/",
        views.agent_invites,
        name="agent_invites"
    ),

]