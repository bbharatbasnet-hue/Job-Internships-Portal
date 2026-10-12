from django.db import migrations
from django.utils.text import slugify
import uuid


def backfill(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    Company = apps.get_model('accounts', 'Company')
    Category = apps.get_model('jobs', 'Category')
    Job = apps.get_model('jobs', 'Job')
    for user in User.objects.filter(role='employer'):
        company, _ = Company.objects.get_or_create(
            employer_id=user.id,
            defaults={'name': user.company or user.get_full_name() or user.username},
        )
        Job.objects.filter(employer_id=user.id, company_profile__isnull=True).update(company_profile_id=company.id)
    for cat in Category.objects.all():
        if not cat.slug:
            cat.slug = slugify(cat.name)
            cat.save(update_fields=['slug'])
    for job in Job.objects.all():
        changed=[]
        if not job.slug:
            job.slug=slugify(f'{job.title}-{uuid.uuid4().hex[:8]}')[:180]; changed.append('slug')
        if job.status == 'published' and not job.is_active:
            job.is_active=True; changed.append('is_active')
        if changed: job.save(update_fields=changed)


def noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies=[('jobs','0002_jobreport_recentlyviewedjob_savedjob_and_more')]
    operations=[migrations.RunPython(backfill, noop)]
