from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from accounts.decorators import role_required
from notifications.models import Notification
from jobs.models import Job
from .forms import ApplicationForm
from .models import Application

@role_required("student")
def apply(request, pk):
    job=get_object_or_404(Job,pk=pk,is_active=True)
    if job.deadline and job.deadline < __import__('django.utils.timezone',fromlist=['localdate']).localdate():
        messages.error(request,"This application deadline has passed."); return redirect(job.get_absolute_url())
    if Application.objects.filter(job=job,student=request.user).exists():
        messages.info(request,"You have already applied to this opportunity."); return redirect(job.get_absolute_url())
    form=ApplicationForm(request.POST or None,request.FILES or None)
    if form.is_valid():
        app=form.save(commit=False); app.job=job; app.student=request.user; app.save()
        Notification.objects.create(recipient=job.employer,title="New application received",message=f"{request.user.display_name} applied for {job.title}.",kind="application",url=f"/applications/job/{job.pk}/")
        messages.success(request,"Application submitted successfully."); return redirect("dashboard")
    return render(request,"applications/apply.html",{"form":form,"job":job})

@role_required("employer")
def review(request, pk):
    job=get_object_or_404(Job,pk=pk,employer=request.user)
    apps=job.applications.select_related("student").all()
    return render(request,"applications/review.html",{"job":job,"apps":apps,"status_choices":Application.STATUS})

@role_required("employer")
@require_POST
def set_status(request, pk):
    app=get_object_or_404(Application,pk=pk,job__employer=request.user)
    new=request.POST.get("status")
    if new not in dict(Application.STATUS): messages.error(request,"Invalid application status."); return redirect("review",pk=app.job_id)
    app.status=new; app.employer_note=request.POST.get("employer_note","")[:5000]; app.save(update_fields=["status","employer_note","updated_at"])
    Notification.objects.create(recipient=app.student,title="Application status updated",message=f"Your application for {app.job.title} is now {app.get_status_display()}.",kind="application",url=app.job.get_absolute_url())
    messages.success(request,"Candidate status updated and the candidate was notified.")
    return redirect("review",pk=app.job_id)

@role_required("student")
@require_POST
def withdraw(request, pk):
    app=get_object_or_404(Application,pk=pk,student=request.user)
    if app.status in {"rejected","selected","withdrawn"}: messages.info(request,"This application can no longer be withdrawn.")
    else: app.status="withdrawn"; app.save(update_fields=["status","updated_at"]); messages.success(request,"Application withdrawn.")
    return redirect("dashboard")


@login_required
def resume_download(request, pk):
    app = get_object_or_404(Application, pk=pk)
    allowed = request.user.is_superuser or app.student_id == request.user.id or app.job.employer_id == request.user.id
    if not allowed:
        return HttpResponseForbidden("You do not have permission to view this resume.")
    return FileResponse(app.resume.open("rb"), as_attachment=True, filename=app.resume.name.rsplit("/",1)[-1])
