# Generated by Django 3.0.14 on 2022-03-27 14:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0037_auto_20220327_1703'),
    ]

    operations = [
        migrations.CreateModel(
            name='DisciplinaProfesorStudent',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('disciplina', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.Disciplina')),
                ('profesor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.Profesor')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='application.Student')),
            ],
        ),
    ]
