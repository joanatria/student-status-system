# Generated by Django 4.2.5 on 2023-12-08 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_app', '0023_remove_subject_units_offeredsubject_lab_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='contact_number',
            field=models.CharField(default='09369216454', max_length=15),
            preserve_default=False,
        ),
    ]