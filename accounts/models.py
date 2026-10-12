from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse
from config.storage import PrivateMediaStorage


class User(AbstractUser):
    STUDENT, EMPLOYER = "student", "employer"
    ROLES = [(STUDENT, "Job Seeker"), (EMPLOYER, "Employer")]

    role = models.CharField(max_length=10, choices=ROLES, default=STUDENT, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=120, blank=True)  # legacy compatibility
    bio = models.TextField(blank=True)
    headline = models.CharField(max_length=160, blank=True)
    location = models.CharField(max_length=160, blank=True)
    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    portfolio = models.URLField(blank=True)
    profile_photo = models.FileField(
        upload_to="profile_photos/",
        blank=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
    )

    @property
    def is_student(self):
        return self.role == self.STUDENT

    @property
    def is_employer(self):
        return self.role == self.EMPLOYER

    @property
    def display_name(self):
        return self.get_full_name().strip() or self.username

    @property
    def profile_completion(self):
        fields = [self.first_name, self.last_name, self.email, self.phone, self.bio, self.location]
        if self.is_student:
            fields.append(self.headline)
        filled = sum(bool(v) for v in fields)
        return min(100, round(filled / len(fields) * 100))


class Company(models.Model):
    SIZE_CHOICES = [
        ("1-10", "1–10"), ("11-50", "11–50"), ("51-200", "51–200"),
        ("201-500", "201–500"), ("500+", "500+")
    ]
    employer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="company_profile")
    name = models.CharField(max_length=160)
    logo = models.FileField(
        upload_to="company_logos/", blank=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp", "svg"])],
    )
    cover_image = models.FileField(
        upload_to="company_covers/", blank=True,
        validators=[FileExtensionValidator(["jpg", "jpeg", "png", "webp"])],
    )
    description = models.TextField(blank=True)
    industry = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=160, blank=True)
    website = models.URLField(blank=True)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, blank=True)
    linkedin = models.URLField(blank=True)
    facebook = models.URLField(blank=True)
    verified = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-featured", "name"]
        indexes = [models.Index(fields=["industry", "location"])]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("company_detail", kwargs={"pk": self.pk})


class Skill(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserSkill(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="users")
    proficiency = models.CharField(max_length=30, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "skill"], name="unique_user_skill")]


class Education(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="education")
    institution = models.CharField(max_length=180)
    degree = models.CharField(max_length=160, blank=True)
    field_of_study = models.CharField(max_length=160, blank=True)
    start_year = models.PositiveIntegerField(null=True, blank=True)
    end_year = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-end_year", "-start_year"]


class Experience(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="experience")
    company = models.CharField(max_length=180)
    title = models.CharField(max_length=160)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["-is_current", "-start_date"]


class Certification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="certifications")
    name = models.CharField(max_length=180)
    issuer = models.CharField(max_length=160, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    credential_url = models.URLField(blank=True)

    class Meta:
        ordering = ["-issue_date"]


class Resume(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resume_profile")
    file = models.FileField(
        upload_to="resumes/",
        storage=PrivateMediaStorage(),
        validators=[FileExtensionValidator(["pdf", "doc", "docx"])],
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume — {self.user.display_name}"
