# Generated by Django 5.0 on 2024-01-12 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_app', '0038_remove_subject_class_code_offeredsubject_class_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='staff_id',
            field=models.CharField(max_length=9),
        ),
    ]
