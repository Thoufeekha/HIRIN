import torch.nn as nn
from django.urls import path
from . import views

urlpatterns = [

    path(
        "",
        views.chatbot_page,
        name="chatbot"
    ),

    path(
        "ask/",
        views.chatbot_api,
        name="chatbot_api"
    ),
]