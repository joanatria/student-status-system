# Generated by Django 4.2.5 on 2023-11-23 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_app', '0019_alter_registration_grade'),
    ]

    operations = [
        migrations.AddField(
            model_name='term',
            name='current_term',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]