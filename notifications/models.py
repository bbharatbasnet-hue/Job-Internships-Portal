from django.conf import settings
from django.db import models

class Notification(models.Model):
    KIND_CHOICES = [("application", "Application"), ("job", "Job"), ("system", "System"), ("interview", "Interview")]
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=160)
    message = models.TextField()
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default="system")
    url = models.CharField(max_length=300, blank=True)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=["-created_at"]
        indexes=[models.Index(fields=["recipient","is_read","created_at"])]
