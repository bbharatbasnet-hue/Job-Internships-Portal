from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, default="fa-briefcase")
    description = models.CharField(max_length=180, blank=True)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self): return self.name


class Job(models.Model):
    TYPES = [("job", "Full-time / Job"), ("internship", "Internship"), ("part_time", "Part-time"), ("contract", "Contract")]
    WORKPLACE = [("onsite", "On-site"), ("hybrid", "Hybrid"), ("remote", "Remote")]
    EXPERIENCE = [("entry", "Entry level"), ("mid", "Mid level"), ("senior", "Senior level"), ("any", "Any experience")]
    STATUS = [("draft", "Draft"), ("pending", "Pending review"), ("published", "Published"), ("closed", "Closed"), ("rejected", "Rejected")]

    employer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="jobs")
    company_profile = models.ForeignKey("accounts.Company", null=True, blank=True, on_delete=models.SET_NULL, related_name="jobs")
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="jobs")
    title = models.CharField(max_length=150, db_index=True)
    company = models.CharField(max_length=120, db_index=True)
    location = models.CharField(max_length=120, db_index=True)
    job_type = models.CharField(max_length=12, choices=TYPES, default="job", db_index=True)
    workplace_type = models.CharField(max_length=10, choices=WORKPLACE, default="onsite")
    experience_level = models.CharField(max_length=10, choices=EXPERIENCE, default="any")
    description = models.TextField()
    responsibilities = models.TextField(blank=True)
    requirements = models.TextField(blank=True)
    qualifications = models.TextField(blank=True)
    skills = models.CharField(max_length=500, blank=True, help_text="Comma-separated skills")
    benefits = models.TextField(blank=True)
    salary = models.CharField(max_length=80, blank=True)
    salary_min = models.PositiveIntegerField(null=True, blank=True)
    salary_max = models.PositiveIntegerField(null=True, blank=True)
    vacancy_count = models.PositiveIntegerField(default=1)
    deadline = models.DateField(null=True, blank=True, db_index=True)
    application_method = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=12, choices=STATUS, default="published", db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)  # legacy compatibility
    featured = models.BooleanField(default=False, db_index=True)
    views = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=180, blank=True, null=True)

    class Meta:
        ordering = ["-featured", "-created"]
        indexes = [
            models.Index(fields=["status", "is_active", "created"]),
            models.Index(fields=["job_type", "workplace_type"]),
            models.Index(fields=["category", "location"]),
        ]

    def save(self, *args, **kwargs):
        if not self.company and self.company_profile_id:
            self.company = self.company_profile.name
        if not self.slug:
            self.slug = slugify(f"{self.title}-{uuid.uuid4().hex[:8]}")[:180]
        self.is_active = self.status == "published" and not self.is_expired
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return bool(self.deadline and self.deadline < timezone.localdate())

    @property
    def skill_list(self):
        return [s.strip() for s in self.skills.split(",") if s.strip()]

    def get_absolute_url(self): return reverse("job_detail", kwargs={"pk": self.pk})
    def __str__(self): return f"{self.title} at {self.company}"


class SavedJob(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_jobs")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "job"], name="unique_saved_job")]
        ordering = ["-created_at"]


class RecentlyViewedJob(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recent_jobs")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="recent_views")
    viewed_at = models.DateTimeField(auto_now=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "job"], name="unique_recent_job")]
        ordering = ["-viewed_at"]


class JobReport(models.Model):
    REASONS = [("spam", "Spam or misleading"), ("fraud", "Potential fraud"), ("duplicate", "Duplicate listing"), ("other", "Other")]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_reports")
    reason = models.CharField(max_length=20, choices=REASONS)
    message = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["-created_at"]
