# Generated by Django 4.2.5 on 2023-12-01 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_app', '0021_remove_offeredsubject_units_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='graded',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='student',
            name='completed_units',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='student',
            name='required_units',
            field=models.IntegerField(default=158),
        ),
        migrations.AddField(
            model_name='student',
            name='years',
            field=models.IntegerField(default=0),
        ),
    ]