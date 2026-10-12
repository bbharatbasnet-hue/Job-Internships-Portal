from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Certification, Company, Education, Experience, Resume, Skill, User, UserSkill

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Profile", {"fields": ("role", "phone", "company", "headline", "location", "bio", "website", "linkedin", "github", "portfolio", "profile_photo")}),)
    list_display = ("username", "email", "role", "company", "is_active", "is_staff")
    list_filter = UserAdmin.list_filter + ("role", "is_active")
    search_fields = ("username", "email", "first_name", "last_name", "company")

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "industry", "location", "verified", "featured", "updated_at")
    list_filter = ("verified", "featured", "industry")
    search_fields = ("name", "industry", "location")

admin.site.register(Skill)
admin.site.register(UserSkill)
admin.site.register(Education)
admin.site.register(Experience)
admin.site.register(Certification)
admin.site.register(Resume)
