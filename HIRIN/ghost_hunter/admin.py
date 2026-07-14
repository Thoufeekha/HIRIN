from django.contrib import admin
from .models import GhostAnalysis
from .service import analyze_job


@admin.action(description="Analyze selected jobs with Ghost Hunter AI")
def analyze_selected(modeladmin, request, queryset):

    for analysis in queryset:
        analyze_job(analysis.job.id)


@admin.register(GhostAnalysis)
class GhostAnalysisAdmin(admin.ModelAdmin):

    list_display = (
        "job",
        "status",
        "confidence",
        "warning_sent",
        "analyzed_at",
    )

    search_fields = (
        "job__title",
        "status",
    )

    list_filter = (
        "status",
        "warning_sent",
    )

    actions = [
        analyze_selected,
    ]