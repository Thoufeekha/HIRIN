# email_generato/admin.py
from django.contrib import admin
from .models import GeneratedDocument

@admin.register(GeneratedDocument)
class GeneratedDocumentAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'job_role', 'user', 'document_type', 'tone', 'created_at']
    list_filter = ['document_type', 'tone', 'created_at']
    search_fields = ['company_name', 'job_role', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Document Information', {
            'fields': ('user', 'company_name', 'job_role', 'recruiter_name', 'tone', 'document_type')
        }),
        ('Generated Content', {
            'fields': ('cover_letter_content', 'cold_email_content')
        }),
        ('Files', {
            'fields': ('cover_letter_pdf', 'cover_letter_docx', 'cold_email_pdf', 'cold_email_docx')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )