from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from accounts.models import Company, User
from applications.models import Application
from jobs.models import Job, SavedJob

@login_required
def home(request):
    u=request.user
    unread=u.notifications.filter(is_read=False).count()
    if u.is_superuser:
        stats={"Users":User.objects.count(),"Employers":User.objects.filter(role="employer").count(),"Active jobs":Job.objects.filter(is_active=True).count(),"Applications":Application.objects.count()}
        from django.db.models.functions import TruncMonth
        monthly=list(Application.objects.annotate(month=TruncMonth("applied_at")).values("month").annotate(total=Count("id")).order_by("-month")[:6])
        ctx={"kind":"admin","stats":stats,"recent":Application.objects.select_related("job","student")[:8],"category_data":list(Job.objects.values("category__name").annotate(total=Count("id")).order_by("-total")[:6]),"monthly_data":monthly}
    elif u.is_employer:
        jobs=u.jobs.annotate(n=Count("applications")); mine=Application.objects.filter(job__employer=u)
        stats={"Listings":jobs.count(),"Applicants":mine.count(),"Awaiting review":mine.filter(status__in=["applied","reviewing"]).count(),"Selected":mine.filter(status="selected").count()}
        ctx={"kind":"employer","jobs":jobs,"stats":stats,"recent_apps":mine.select_related("student","job")[:8]}
    else:
        apps=u.applications.select_related("job"); saved=SavedJob.objects.filter(user=u).select_related("job")
        stats={"Applications":apps.count(),"In review":apps.filter(status__in=["applied","reviewing","shortlisted","interview"]).count(),"Selected":apps.filter(status="selected").count(),"Saved jobs":saved.count()}
        recommended=Job.objects.filter(is_active=True).select_related("category").exclude(applications__student=u).order_by("-featured","-created")[:6]
        if u.location:
            recommended=Job.objects.filter(is_active=True).filter(location__icontains=u.location.split(",")[0]).exclude(applications__student=u).select_related("category")[:6] or recommended
        ctx={"kind":"student","apps":apps[:8],"saved":saved[:6],"stats":stats,"profile_completion":u.profile_completion,"recent_jobs":u.recent_jobs.select_related("job")[:4],"recommended_jobs":recommended}
    ctx["unread_notifications"]=unread
    return render(request,"dashboard/home.html",ctx)
