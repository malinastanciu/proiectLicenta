# Generated by Django 3.0.14 on 2022-06-02 16:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0045_grupaproiect'),
    ]

    operations = [
        migrations.AddField(
            model_name='proiect',
            name='distribuire_teme',
            field=models.BooleanField(default=False),
        ),
        migrations.DeleteModel(
            name='GrupaProiect',
        ),
    ]
