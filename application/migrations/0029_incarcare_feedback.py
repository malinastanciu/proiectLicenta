# Generated by Django 3.0.14 on 2022-03-21 15:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0028_task_student'),
    ]

    operations = [
        migrations.AddField(
            model_name='incarcare',
            name='feedback',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
