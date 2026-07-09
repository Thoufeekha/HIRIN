# email_generato/urls.py
from django.urls import path
from email_generato import views



urlpatterns = [
    path('', views.email_generator_home, name='home'),
    path('generate/', views.generate_document, name='generate'),
    path('view/<int:doc_id>/', views.view_document, name='view_document'),
    path('download/<int:doc_id>/<str:doc_type>/<str:file_format>/', 
         views.download_file, name='download_file'),
    path('delete/<int:doc_id>/', views.delete_document, name='delete_document'),
]