from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from .models import Notification

@login_required
def list_notifications(request):
    items=Notification.objects.filter(recipient=request.user)
    return render(request,"notifications/list.html",{"notifications":items})

@login_required
@require_POST
def mark_read(request, pk):
    Notification.objects.filter(pk=pk, recipient=request.user).update(is_read=True)
    return redirect(request.POST.get("next") or "notifications")

@login_required
@require_POST
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect(request.POST.get("next") or "notifications")
