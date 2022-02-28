from django.db import models
from django.contrib.auth.models import Group, User


# Create your models here.
class Disciplina(models.Model):
    id = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=100)
    profesor = models.ForeignKey(User, on_delete=models.CASCADE)


class Proiect(models.Model):
    id = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=100)
    data_inregistare = models.DateField(auto_now_add=True)
    data_finalizare = models.DateField()
    profesor = models.ForeignKey(User, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, null=True)
    cale = models.CharField(max_length=100, default=None)


class Student(models.Model):
    pass
