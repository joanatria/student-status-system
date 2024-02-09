# Generated by Django 4.2.5 on 2023-10-19 11:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_app', '0009_alter_term_end_date_alter_term_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('ADMIN', 'Admin'), ('STAFF', 'Staff'), ('THESIS ADVISOR', 'Thesis Advisor'), ('PROGRAM ADVISOR', 'Program Advisor'), ('NON ADVISOR FACULTY', 'Faculty')], max_length=50),
        ),
        migrations.DeleteModel(
            name='StudyPlanRecord',
        ),
    ]
