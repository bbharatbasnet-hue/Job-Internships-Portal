from django import forms
from django.utils import timezone
from .models import Job, JobReport

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ("title", "category", "description", "responsibilities", "requirements", "qualifications", "skills", "job_type", "workplace_type", "location", "salary", "salary_min", "salary_max", "experience_level", "vacancy_count", "deadline", "benefits", "application_method", "status")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 7}), "responsibilities": forms.Textarea(attrs={"rows": 5}),
            "requirements": forms.Textarea(attrs={"rows": 5}), "qualifications": forms.Textarea(attrs={"rows": 4}),
            "benefits": forms.Textarea(attrs={"rows": 4}), "application_method": forms.Textarea(attrs={"rows": 3}),
            "deadline": forms.DateInput(attrs={"type": "date"}), "skills": forms.TextInput(attrs={"placeholder": "Python, Django, SQL"}),
        }

    def clean_deadline(self):
        value = self.cleaned_data.get("deadline")
        if value and value < timezone.localdate():
            raise forms.ValidationError("Application deadline cannot be in the past.")
        return value

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("status") == "published" and not cleaned.get("description"):
            self.add_error("description", "A description is required before publishing.")
        return cleaned

class JobReportForm(forms.ModelForm):
    class Meta:
        model = JobReport
        fields = ("reason", "message")
        widgets = {"message": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell us what looks wrong…"})}
