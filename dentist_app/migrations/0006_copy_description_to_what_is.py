from django.db import migrations


def copy_description_to_what_is(apps, schema_editor):
    Service = apps.get_model('dentist_app', 'Service')
    for s in Service.objects.all():
        if s.what_is in (None, '') and s.description:
            s.what_is = s.description
            s.save(update_fields=['what_is'])


class Migration(migrations.Migration):

    dependencies = [
        ('dentist_app', '0005_service_what_is_service_when_to_do_and_more'),
    ]

    operations = [
        migrations.RunPython(copy_description_to_what_is, migrations.RunPython.noop),
    ]
