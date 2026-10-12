from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST
from accounts.decorators import role_required
from accounts.models import Company
from notifications.models import Notification
from .forms import JobForm, JobReportForm
from .models import Category, Job, RecentlyViewedJob, SavedJob


def home(request):
    featured = Job.objects.filter(is_active=True, featured=True).select_related("category", "company_profile")[:6]
    latest = Job.objects.filter(is_active=True).select_related("category", "company_profile")[:8]
    categories = Category.objects.annotate(active_jobs=Count("jobs", filter=Q(jobs__is_active=True))).order_by("-active_jobs", "name")[:8]
    companies = Company.objects.filter(employer__is_active=True, featured=True).select_related("employer")[:6]
    stats = {
        "jobs": Job.objects.filter(is_active=True).count(),
        "companies": Company.objects.filter(employer__is_active=True).count(),
        "applications": __import__("applications.models", fromlist=["Application"]).Application.objects.count(),
        "categories": Category.objects.count(),
    }
    return render(request, "home.html", {"featured_jobs": featured, "latest_jobs": latest, "categories": categories, "companies": companies, "stats": stats})


def job_list(request):
    jobs = Job.objects.filter(is_active=True).select_related("category", "company_profile")
    p = request.GET
    q, location, category, kind, workplace = p.get("q", "").strip(), p.get("location", "").strip(), p.get("category", ""), p.get("type", ""), p.get("workplace", "")
    experience, salary, company, posted, sort = p.get("experience", ""), p.get("salary", ""), p.get("company", "").strip(), p.get("posted", ""), p.get("sort", "newest")
    min_salary, max_salary = p.get("min_salary", ""), p.get("max_salary", "")
    if q: jobs = jobs.filter(Q(title__icontains=q) | Q(company__icontains=q) | Q(description__icontains=q) | Q(skills__icontains=q))
    if location: jobs = jobs.filter(location__icontains=location)
    if category: jobs = jobs.filter(category_id=category)
    if kind: jobs = jobs.filter(job_type=kind)
    if workplace: jobs = jobs.filter(workplace_type=workplace)
    if experience: jobs = jobs.filter(experience_level=experience)
    if company: jobs = jobs.filter(company__icontains=company)
    if min_salary.isdigit(): jobs = jobs.filter(salary_max__gte=int(min_salary))
    if max_salary.isdigit(): jobs = jobs.filter(salary_min__lte=int(max_salary))
    if posted == "24h": jobs = jobs.filter(created__gte=timezone.now() - timezone.timedelta(hours=24))
    elif posted == "7d": jobs = jobs.filter(created__gte=timezone.now() - timezone.timedelta(days=7))
    elif posted == "30d": jobs = jobs.filter(created__gte=timezone.now() - timezone.timedelta(days=30))
    if sort == "oldest": jobs = jobs.order_by("created")
    elif sort == "deadline": jobs = jobs.order_by("deadline", "-created")
    elif sort == "views": jobs = jobs.order_by("-views", "-created")
    else: jobs = jobs.order_by("-featured", "-created")
    page = Paginator(jobs, 10).get_page(p.get("page"))
    saved_ids = set()
    if request.user.is_authenticated and request.user.is_student:
        saved_ids = set(SavedJob.objects.filter(user=request.user, job__in=page.object_list).values_list("job_id", flat=True))
    return render(request, "jobs/list.html", {"jobs": page, "categories": Category.objects.all(), "saved_ids": saved_ids})


def job_detail(request, pk):
    job = get_object_or_404(Job.objects.select_related("category", "company_profile", "employer"), pk=pk)
    if not job.is_active and not (request.user.is_authenticated and (request.user.is_superuser or job.employer_id == request.user.id)):
        return render(request, "jobs/closed.html", {"job": job}, status=410)
    Job.objects.filter(pk=pk).update(views=job.views + 1)
    applied = request.user.is_authenticated and job.applications.filter(student=request.user).exists()
    saved = request.user.is_authenticated and SavedJob.objects.filter(user=request.user, job=job).exists()
    if request.user.is_authenticated and request.user.is_student:
        RecentlyViewedJob.objects.update_or_create(user=request.user, job=job)
    similar = Job.objects.filter(is_active=True).exclude(pk=job.pk)
    if job.category_id: similar = similar.filter(category_id=job.category_id)
    similar = similar[:4]
    return render(request, "jobs/detail.html", {"job": job, "applied": applied, "saved": saved, "similar": similar, "report_form": JobReportForm()})


@role_required("student")
@require_POST
def toggle_save(request, pk):
    job = get_object_or_404(Job, pk=pk, is_active=True)
    obj, created = SavedJob.objects.get_or_create(user=request.user, job=job)
    if not created: obj.delete()
    messages.success(request, "Job saved." if created else "Job removed from saved jobs.")
    return redirect(request.POST.get("next") or job.get_absolute_url())


@role_required("student")
@require_POST
def report_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    form = JobReportForm(request.POST)
    if form.is_valid():
        report = form.save(commit=False); report.job=job; report.reporter=request.user; report.save()
        messages.success(request, "Thanks. Your report has been submitted for review.")
    return redirect(job.get_absolute_url())


@role_required("employer")
def job_create(request):
    company = getattr(request.user, "company_profile", None)
    form = JobForm(request.POST or None, initial={"company": request.user.company, "status": "published"})
    if form.is_valid():
        job = form.save(commit=False); job.employer=request.user; job.company_profile=company
        job.company = company.name if company else request.user.company
        job.save(); messages.success(request, "Your vacancy is now live."); return redirect("dashboard")
    return render(request, "jobs/form.html", {"form": form, "title": "Create a new opportunity", "button": "Publish opportunity"})


@role_required("employer")
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user)
    form = JobForm(request.POST or None, instance=job)
    if form.is_valid(): form.save(); messages.success(request, "Opportunity updated."); return redirect("dashboard")
    return render(request, "jobs/form.html", {"form": form, "title": "Edit opportunity", "button": "Save changes", "job": job})


@role_required("employer")
@require_POST
def job_delete(request, pk):
    job=get_object_or_404(Job, pk=pk, employer=request.user); job.status="closed"; job.is_active=False; job.save(update_fields=["status","is_active","updated"])
    messages.success(request, "Opportunity closed."); return redirect("dashboard")


@login_required
def saved_jobs(request):
    page=Paginator(SavedJob.objects.filter(user=request.user).select_related("job","job.category"), 10).get_page(request.GET.get("page"))
    return render(request,"jobs/saved.html",{"saved_jobs":page})
