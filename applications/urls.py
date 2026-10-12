from django.urls import path
from . import views
urlpatterns=[path("apply/<int:pk>/",views.apply,name="apply"),path("job/<int:pk>/",views.review,name="review"),path("status/<int:pk>/",views.set_status,name="set_status"),path("<int:pk>/withdraw/",views.withdraw,name="withdraw_application"),path("<int:pk>/resume/",views.resume_download,name="application_resume_download")]
