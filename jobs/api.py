from django.db.models import Q
from rest_framework import serializers, viewsets
from rest_framework.permissions import SAFE_METHODS, BasePermission
from .models import Category, Job
class CategorySerializer(serializers.ModelSerializer):
 class Meta: model=Category; fields=("id","name","slug","icon")
class JobSerializer(serializers.ModelSerializer):
 category_name=serializers.CharField(source="category.name",read_only=True)
 class Meta:
  model=Job; fields=("id","title","company","location","job_type","workplace_type","experience_level","description","requirements","qualifications","skills","salary","deadline","vacancy_count","status","featured","created","updated","category","category_name"); read_only_fields=("employer","company","created","updated","views")
class IsEmployerOrReadOnly(BasePermission):
 def has_permission(self,request,view): return request.method in SAFE_METHODS or (request.user.is_authenticated and request.user.is_employer)
 def has_object_permission(self,request,view,obj): return request.method in SAFE_METHODS or obj.employer_id==request.user.id
class JobViewSet(viewsets.ModelViewSet):
 serializer_class=JobSerializer; permission_classes=[IsEmployerOrReadOnly]
 def get_queryset(self):
  qs=Job.objects.filter(is_active=True).select_related("category")
  p=self.request.query_params
  if p.get("q"): qs=qs.filter(Q(title__icontains=p["q"])|Q(company__icontains=p["q"])|Q(location__icontains=p["q"])|Q(skills__icontains=p["q"]))
  if p.get("category"): qs=qs.filter(category_id=p["category"])
  if p.get("type"): qs=qs.filter(job_type=p["type"])
  if p.get("workplace"): qs=qs.filter(workplace_type=p["workplace"])
  return qs
 def perform_create(self,serializer): serializer.save(employer=self.request.user,status="published",is_active=True)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet): queryset=Category.objects.all(); serializer_class=CategorySerializer; pagination_class=None
