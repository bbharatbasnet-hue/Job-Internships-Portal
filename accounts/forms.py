from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Company, Education, Experience, Resume, User

MAX_UPLOAD = 5 * 1024 * 1024


def validate_upload_size(file):
    if file and file.size > MAX_UPLOAD:
        raise ValidationError("File size must be 5 MB or smaller.")


class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name", "role", "company")

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "email", "phone", "headline", "location", "bio",
            "website", "linkedin", "github", "portfolio", "profile_photo",
        )
        widgets = {"bio": forms.Textarea(attrs={"rows": 5}), "profile_photo": forms.ClearableFileInput()}

    def clean_profile_photo(self):
        value = self.cleaned_data.get("profile_photo")
        if value and hasattr(value, "size") and value.size > MAX_UPLOAD:
            raise forms.ValidationError("Profile photo must be 5 MB or smaller.")
        return value


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ("file",)
        widgets = {"file": forms.ClearableFileInput(attrs={"accept": ".pdf,.doc,.docx"})}

    def clean_file(self):
        value = self.cleaned_data["file"]
        validate_upload_size(value)
        return value


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        exclude = ("employer", "verified", "featured")
        widgets = {"description": forms.Textarea(attrs={"rows": 6})}

    def clean(self):
        data = super().clean()
        for key in ("logo", "cover_image"):
            value = data.get(key)
            if value and hasattr(value, "size") and value.size > MAX_UPLOAD:
                self.add_error(key, "Image must be 5 MB or smaller.")
        return data


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        exclude = ("user",)


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        exclude = ("user",)
        widgets = {"start_date": forms.DateInput(attrs={"type": "date"}), "end_date": forms.DateInput(attrs={"type": "date"}), "description": forms.Textarea(attrs={"rows": 4})}


class ProfileSectionForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ("company", "title", "start_date", "end_date", "is_current", "description")
