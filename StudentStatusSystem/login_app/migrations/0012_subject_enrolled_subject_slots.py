# Generated by Django 4.2.5 on 2023-10-20 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_app', '0011_student_birthday_student_contact_number_student_sex_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='enrolled',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='subject',
            name='slots',
            field=models.IntegerField(default=25),
        ),
    ]