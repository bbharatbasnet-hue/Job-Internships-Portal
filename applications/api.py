from rest_framework import mixins, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from notifications.models import Notification
from .models import Application
class ApplicationSerializer(serializers.ModelSerializer):
 class Meta:
  model=Application; fields=("id","job","student","resume","cover_letter","status","employer_note","interview_at","applied_at","updated_at"); read_only_fields=("student","status","employer_note","applied_at","updated_at")
class ApplicationViewSet(mixins.CreateModelMixin,mixins.ListModelMixin,mixins.RetrieveModelMixin,viewsets.GenericViewSet):
 serializer_class=ApplicationSerializer; permission_classes=[IsAuthenticated]
 def get_queryset(self):
  u=self.request.user
  return Application.objects.filter(job__employer=u) if u.is_employer else Application.objects.filter(student=u)
 def perform_create(self,serializer):
  u=self.request.user
  if not u.is_student: raise PermissionDenied("Only job seekers can apply.")
  job=serializer.validated_data["job"]
  if not job.is_active: raise ValidationError("This opportunity is not accepting applications.")
  if Application.objects.filter(job=job,student=u).exists(): raise ValidationError("You have already applied to this job.")
  serializer.save(student=u,status="applied")
 @action(detail=True,methods=["post"])
 def set_status(self,request,pk=None):
  if not request.user.is_employer: raise PermissionDenied("Only employers can change status.")
  app=self.get_object(); new=request.data.get("status")
  if app.job.employer_id!=request.user.id: raise PermissionDenied()
  if new not in dict(Application.STATUS): raise ValidationError({"status":"Invalid status."})
  app.status=new; app.save(update_fields=["status","updated_at"]); Notification.objects.create(recipient=app.student,title="Application status updated",message=f"Your application for {app.job.title} is now {app.get_status_display()}.",kind="application",url=app.job.get_absolute_url())
  return Response(ApplicationSerializer(app).data)
