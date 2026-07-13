from django.contrib import admin

admin.site.site_header = "HIRIN Administration"
admin.site.site_title = "HIRIN Admin"
admin.site.index_title = "Welcome to HIRIN Admin Panel"
# Register your models here.
from django.contrib import admin
from .models import *

admin.site.register(JobSeekerProfile)
admin.site.register(RecruiterProfile)
admin.site.register(UserRole)
admin.site.register(Job)
admin.site.register(Application)