from django.contrib import admin
from .models import Category, Job, JobReport, RecentlyViewedJob, SavedJob
admin.site.register(Category)
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display=("title","company","job_type","status","featured","deadline","created")
    list_filter=("status","job_type","workplace_type","experience_level","featured","category")
    search_fields=("title","company","location","skills")
    list_editable=("status","featured")
@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin): list_display=("user","job","created_at")
admin.site.register(RecentlyViewedJob)
@admin.register(JobReport)
class JobReportAdmin(admin.ModelAdmin):
    list_display=("job","reporter","reason","resolved","created_at")
    list_filter=("reason","resolved")
    list_editable=("resolved",)
