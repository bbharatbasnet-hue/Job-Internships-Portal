from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("resume/upload/", views.resume_upload, name="resume_upload"),
    path("resume/builder/", views.resume_builder, name="resume_builder"),
    path("resume/<int:pk>/download/", views.resume_download, name="resume_download"),
    path("company/", views.company_profile, name="company_profile"),
    path("education/add/", views.education_add, name="education_add"),
    path("experience/add/", views.experience_add, name="experience_add"),
]
