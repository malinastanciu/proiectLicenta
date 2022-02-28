from django.db import models
from django.contrib.auth.models import Group, User
from django.contrib.postgres.fields import ArrayField


# Create your models here.
class Proiect(models.Model):
    id = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=100)
    data_inregistare = models.DateField(auto_now_add=True)
    data_finalizare = models.DateField()
    profesor = models.ForeignKey(User, on_delete=models.CASCADE)
    cale = models.CharField(max_length=100, default=None)


class Disciplina(models.Model):
    id = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=100)
    proiecte = models.ManyToManyField(Proiect)
    profesor = models.ForeignKey(User, on_delete=models.CASCADE)
