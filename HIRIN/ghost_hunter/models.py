from django.db import models
from accounts.models import Job


class GhostAnalysis(models.Model):

    STATUS_CHOICES = [
        ("Safe", "Safe"),
        ("Warning", "Warning"),
        ("Deleted", "Deleted"),
    ]

    job = models.OneToOneField(
        Job,
        on_delete=models.CASCADE,
        related_name="ghost_analysis"
    )

    confidence = models.PositiveIntegerField(
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Safe"
    )

    reasoning = models.TextField(
        blank=True,
        default=""
    )

    warning_sent = models.BooleanField(
        default=False
    )

    analyzed_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-analyzed_at"]
        verbose_name = "Ghost Analysis"
        verbose_name_plural = "Ghost Analyses"

    def __str__(self):
        return f"{self.job.title} ({self.status} - {self.confidence}%)"