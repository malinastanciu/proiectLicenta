# Generated by Django 3.0.14 on 2022-03-14 17:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0025_student_teme'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proiect',
            name='distribuire_teme',
        ),
    ]
