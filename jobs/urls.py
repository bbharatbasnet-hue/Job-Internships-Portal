from django.urls import path
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("jobs/", views.job_list, name="job_list"),
    path("jobs/<int:pk>/", views.job_detail, name="job_detail"),
    path("jobs/<int:pk>/save/", views.toggle_save, name="toggle_save"),
    path("jobs/<int:pk>/report/", views.report_job, name="report_job"),
    path("jobs/new/", views.job_create, name="job_create"),
    path("jobs/<int:pk>/edit/", views.job_edit, name="job_edit"),
    path("jobs/<int:pk>/delete/", views.job_delete, name="job_delete"),
    path("saved/", views.saved_jobs, name="saved_jobs"),
]
