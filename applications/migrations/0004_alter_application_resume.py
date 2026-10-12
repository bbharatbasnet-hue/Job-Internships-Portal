import os
import shutil
from django.conf import settings
import config.storage
import django.core.validators
from django.db import migrations, models

def move_existing_application_resumes(apps, schema_editor):
    Application=apps.get_model('applications','Application')
    source_root=settings.MEDIA_ROOT
    target_root=settings.PRIVATE_MEDIA_ROOT
    os.makedirs(os.path.join(target_root,'application_resumes'),exist_ok=True)
    for obj in Application.objects.exclude(resume=''):
        old_name=obj.resume.name
        src=os.path.join(source_root,old_name)
        if not os.path.exists(src):
            continue
        name=os.path.basename(old_name)
        dest_name=os.path.join('application_resumes',name).replace('\\','/')
        dest=os.path.join(target_root,dest_name)
        if not os.path.exists(dest): shutil.copy2(src,dest)
        obj.resume.name=dest_name
        obj.save(update_fields=['resume'])

class Migration(migrations.Migration):
    dependencies=[('applications','0003_migrate_application_statuses')]
    operations=[
        migrations.RunPython(move_existing_application_resumes,migrations.RunPython.noop),
        migrations.AlterField(model_name='application',name='resume',field=models.FileField(storage=config.storage.PrivateMediaStorage(),upload_to='application_resumes/',validators=[django.core.validators.FileExtensionValidator(['pdf','doc','docx'])])),
    ]
