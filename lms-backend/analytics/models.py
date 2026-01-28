from django.db import models

class AnalyticsLog(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Analytics Log"
        verbose_name_plural = "Analytics Logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Log: {self.message}"
