from django.db import models


class GhostAnalysis(models.Model):
    STATUS_CHOICES = [
        ("Safe", "Safe"),
        ("Warning", "Warning"),
        ("Deleted", "Deleted"),
    ]

    job_id = models.IntegerField(unique=True)

    confidence = models.IntegerField(default=0)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Safe"
    )

    reasoning = models.TextField()

    warning_sent = models.BooleanField(default=False)

    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Job {self.job_id} - {self.status}"