from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from jobs.models import Job
from config.storage import PrivateMediaStorage

class Application(models.Model):
    STATUS = [("applied","Applied"),("reviewing","Reviewing"),("shortlisted","Shortlisted"),("interview","Interview"),("selected","Selected"),("rejected","Rejected"),("withdrawn","Withdrawn")]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications")
    resume = models.FileField(upload_to="application_resumes/", storage=PrivateMediaStorage(), validators=[FileExtensionValidator(["pdf","doc","docx"])])
    cover_letter = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default="applied", db_index=True)
    employer_note = models.TextField(blank=True)
    interview_at = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering=["-applied_at"]
        constraints=[models.UniqueConstraint(fields=["job","student"],name="unique_application_job_student")]
        indexes=[models.Index(fields=["job","status"]),models.Index(fields=["student","status"])]
    def __str__(self): return f"{self.student} -> {self.job}"
    @property
    def is_active(self): return self.status not in {"rejected","withdrawn","selected"}
