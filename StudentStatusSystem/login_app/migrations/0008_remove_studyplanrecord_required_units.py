# Generated by Django 4.2.5 on 2023-09-29 21:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login_app', '0007_studyplanrecord_required_units'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studyplanrecord',
            name='required_units',
        ),
    ]