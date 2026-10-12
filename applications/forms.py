from django import forms
from django.core.exceptions import ValidationError
from .models import Application
MAX_UPLOAD=5*1024*1024
class ApplicationForm(forms.ModelForm):
    class Meta:
        model=Application; fields=("resume","cover_letter")
        widgets={"cover_letter":forms.Textarea(attrs={"rows":7,"placeholder":"Tell the employer why you are a strong fit…"}),"resume":forms.ClearableFileInput(attrs={"accept":".pdf,.doc,.docx"})}
    def clean_resume(self):
        f=self.cleaned_data["resume"]
        if f.size>MAX_UPLOAD: raise ValidationError("Resume must be 5 MB or smaller.")
        return f
