# Generated by Django 4.2.5 on 2023-10-21 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_app', '0015_rename_student_id_registration_student_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='completion',
            field=models.CharField(blank=True, choices=[('PASSED', 'Passed'), ('INCOMPLETE', 'Incomplete'), ('FAILED', 'Failed')], max_length=200),
        ),
        migrations.AlterField(
            model_name='registration',
            name='grade',
            field=models.IntegerField(choices=[(1, '1.0'), (1.25, '1.25'), (1.5, '1.5'), (1.75, '1.75'), (2.0, '2.0'), (2.25, '2.25'), (2.5, '2.5'), (2.75, '2.75'), (3, '3.0'), (4, '4.0'), (5, '5.0'), (0, 'INC')], default=0),
        ),
    ]
