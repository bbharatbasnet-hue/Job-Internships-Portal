import os
import shutil
from django.conf import settings
import config.storage
import django.core.validators
from django.db import migrations, models

def move_existing_resumes(apps, schema_editor):
    Resume=apps.get_model('accounts','Resume')
    source_root=settings.MEDIA_ROOT
    target_root=settings.PRIVATE_MEDIA_ROOT
    os.makedirs(os.path.join(target_root,'resumes'),exist_ok=True)
    for obj in Resume.objects.exclude(file=''):
        old_name=obj.file.name
        src=os.path.join(source_root,old_name)
        if not os.path.exists(src):
            continue
        name=os.path.basename(old_name)
        dest_name=os.path.join('resumes',name).replace('\\','/')
        dest=os.path.join(target_root,dest_name)
        if not os.path.exists(dest): shutil.copy2(src,dest)
        obj.file.name=dest_name
        obj.save(update_fields=['file'])

class Migration(migrations.Migration):
    dependencies=[('accounts','0002_skill_user_github_user_headline_user_linkedin_and_more')]
    operations=[
        migrations.RunPython(move_existing_resumes,migrations.RunPython.noop),
        migrations.AlterField(model_name='resume',name='file',field=models.FileField(storage=config.storage.PrivateMediaStorage(),upload_to='resumes/',validators=[django.core.validators.FileExtensionValidator(['pdf','doc','docx'])])),
    ]
