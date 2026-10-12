from django.db import migrations

def forwards(apps, schema_editor):
    Application=apps.get_model('applications','Application')
    Application.objects.filter(status='pending').update(status='applied')
    Application.objects.filter(status='reviewed').update(status='reviewing')
    Application.objects.filter(status='accepted').update(status='selected')

def backwards(apps, schema_editor):
    Application=apps.get_model('applications','Application')
    Application.objects.filter(status='applied').update(status='pending')
    Application.objects.filter(status='reviewing').update(status='reviewed')
    Application.objects.filter(status='selected').update(status='accepted')

class Migration(migrations.Migration):
    dependencies=[('applications','0002_alter_application_unique_together_and_more')]
    operations=[migrations.RunPython(forwards, backwards)]
