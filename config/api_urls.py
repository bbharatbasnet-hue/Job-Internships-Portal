from django.urls import include, path
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from applications.api import ApplicationViewSet
from jobs.api import CategoryViewSet, JobViewSet

router = DefaultRouter()
router.register("jobs", JobViewSet, basename="api-job")
router.register("categories", CategoryViewSet, basename="api-category")
router.register("applications", ApplicationViewSet, basename="api-application")

urlpatterns = [
    path("token/", obtain_auth_token),   # POST username+password -> {"token": "..."}
    path("", include(router.urls)),
]
