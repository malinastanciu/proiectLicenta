# Generated by Django 3.0.14 on 2022-01-08 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0004_auto_20220108_1551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='path',
            field=models.CharField(default=None, max_length=100),
        ),
    ]
