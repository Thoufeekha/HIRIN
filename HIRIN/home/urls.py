from django.urls import path,include
from . import views
# urlpatterns = [
#     path('', views.index),
#     path('companies/', views.companies),
#     # path('service/', views.service),
#     path('login/', views.login),
#     path('signup/', views.signup),
#     path('getstarted/', views.getstarted),
# ]
urlpatterns = [
    path('', views.index, name='home'),
    path('companies/', views.companies, name='companies'),
    path('FAQ/', views.FAQ, name='FAQ'),
    path('login/', views.login, name='login'),
    # path('signup/', views.signup, name='signup'),
    path('getstarted/', views.getstarted, name='getstarted'),
]
