from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .forms import CompanyForm, EducationForm, ExperienceForm, ProfileForm, RegisterForm, ResumeForm
from .models import Company, Education, Experience, Resume, User


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        if user.is_employer:
            Company.objects.create(employer=user, name=user.company or user.get_full_name() or user.username)
        login(request, user)
        messages.success(request, "Welcome! Your account is ready.")
        return redirect("dashboard")
    return render(request, "registration/register.html", {"form": form})


@login_required
def profile(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("profile")
    resume = getattr(request.user, "resume_profile", None)
    return render(request, "accounts/profile.html", {"form": form, "resume": resume})


@login_required
@require_POST
def resume_upload(request):
    form = ResumeForm(request.POST, request.FILES, instance=getattr(request.user, "resume_profile", None))
    if form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.save()
        messages.success(request, "Resume uploaded successfully.")
    else:
        messages.error(request, form.errors.get("file", ["Please choose a valid resume."])[0])
    return redirect("profile")


@login_required
def resume_download(request, pk):
    resume = get_object_or_404(Resume, pk=pk)
    allowed = request.user.is_superuser or resume.user_id == request.user.id or (
        request.user.is_employer and resume.user.applications.filter(job__employer=request.user).exists()
    )
    if not allowed:
        return HttpResponseForbidden("You do not have permission to view this resume.")
    if not resume.file:
        raise Http404("Resume not found.")
    return FileResponse(resume.file.open("rb"), as_attachment=True, filename=resume.file.name.rsplit("/", 1)[-1])


@login_required
def company_profile(request):
    if not request.user.is_employer and not request.user.is_superuser:
        return HttpResponseForbidden("Employer access required.")
    company, _ = Company.objects.get_or_create(
        employer=request.user,
        defaults={"name": request.user.company or request.user.get_full_name() or request.user.username},
    )
    form = CompanyForm(request.POST or None, request.FILES or None, instance=company)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.employer = request.user
        obj.save()
        request.user.company = obj.name
        request.user.save(update_fields=["company"])
        messages.success(request, "Company profile updated.")
        return redirect("company_profile")
    return render(request, "accounts/company_form.html", {"form": form, "company": company})


def company_list(request):
    qs = Company.objects.filter(employer__is_active=True).select_related("employer")
    q, industry, location = request.GET.get("q", "").strip(), request.GET.get("industry", "").strip(), request.GET.get("location", "").strip()
    if q:
        qs = qs.filter(name__icontains=q) | qs.filter(description__icontains=q)
    if industry:
        qs = qs.filter(industry__icontains=industry)
    if location:
        qs = qs.filter(location__icontains=location)
    page = Paginator(qs.distinct(), 12).get_page(request.GET.get("page"))
    industries = Company.objects.exclude(industry="").values_list("industry", flat=True).distinct().order_by("industry")
    return render(request, "companies/list.html", {"companies": page, "industries": industries})


def company_detail(request, pk):
    company = get_object_or_404(Company.objects.select_related("employer"), pk=pk)
    jobs = company.employer.jobs.filter(is_active=True).select_related("category")
    return render(request, "companies/detail.html", {"company": company, "jobs": jobs})


@login_required
@require_POST
def education_add(request):
    form = EducationForm(request.POST)
    if form.is_valid():
        obj = form.save(commit=False); obj.user = request.user; obj.save()
        messages.success(request, "Education added.")
    return redirect("profile")


@login_required
@require_POST
def experience_add(request):
    form = ExperienceForm(request.POST)
    if form.is_valid():
        obj = form.save(commit=False); obj.user = request.user; obj.save()
        messages.success(request, "Experience added.")
    return redirect("profile")


@login_required
def resume_builder(request):
    return render(request, "accounts/resume_builder.html", {
        "candidate": request.user,
        "education": request.user.education.all(),
        "experience": request.user.experience.all(),
        "certifications": request.user.certifications.all(),
        "skills": request.user.skills.select_related("skill").all(),
    })
