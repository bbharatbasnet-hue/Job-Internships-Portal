from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from .models import User
from jobs.models import Category, Job, SavedJob
from applications.models import Application

class PlatformFlowTests(TestCase):
    def setUp(self):
        self.employer=User.objects.create_user(username='employer',password='pass12345',role='employer',company='Test Co',email='hr@test.example')
        self.student=User.objects.create_user(username='student',password='pass12345',role='student',email='student@test.example')
        self.category=Category.objects.create(name='Engineering')
        self.job=Job.objects.create(employer=self.employer,company='Test Co',category=self.category,title='Django Developer',location='Kathmandu',job_type='job',description='Build web applications',status='published',is_active=True)

    def test_public_discovery(self):
        self.assertEqual(self.client.get(reverse('home')).status_code,200)
        self.assertEqual(self.client.get(reverse('job_list')+'?q=Django').status_code,200)
        self.assertEqual(self.client.get(self.job.get_absolute_url()).status_code,200)

    def test_student_save_and_apply(self):
        self.client.login(username='student',password='pass12345')
        self.client.post(reverse('toggle_save',args=[self.job.pk]),{'next':self.job.get_absolute_url()})
        self.assertTrue(SavedJob.objects.filter(user=self.student,job=self.job).exists())
        pdf=SimpleUploadedFile('resume.pdf',b'%PDF-1.4 demo',content_type='application/pdf')
        r=self.client.post(reverse('apply',args=[self.job.pk]),{'resume':pdf,'cover_letter':'I am a strong fit.'})
        self.assertEqual(r.status_code,302)
        app=Application.objects.get(job=self.job,student=self.student)
        self.assertEqual(app.status,'applied')
        self.assertEqual(self.employer.notifications.count(),1)

    def test_employer_cannot_access_other_job_management(self):
        other=User.objects.create_user(username='other',password='pass12345',role='employer')
        self.client.login(username='other',password='pass12345')
        self.assertEqual(self.client.get(reverse('job_edit',args=[self.job.pk])).status_code,404)
