from django.contrib import admin
from .models import GhostAnalysis


@admin.register(GhostAnalysis)
class GhostAnalysisAdmin(admin.ModelAdmin):
    list_display = (
        "job_id",
        "status",
        "confidence",
        "warning_sent",
        "analyzed_at",
    )

    search_fields = ("job_id", "status")

    list_filter = (
        "status",
        "warning_sent",
    )