# Generated by Django 4.2.5 on 2023-10-21 00:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('login_app', '0014_alter_student_middle_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='registration',
            old_name='student_id',
            new_name='student',
        ),
        migrations.RenameField(
            model_name='registration',
            old_name='subject_id',
            new_name='subject',
        ),
        migrations.RenameField(
            model_name='subject',
            old_name='term_id',
            new_name='term',
        ),
    ]
