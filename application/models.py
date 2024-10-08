from django.db import models
from django.contrib.auth.models import Group, User


# Create your models here.
class Grupa(models.Model):
    id = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=10, null=True, unique=True)
    asignare_discipline = models.BooleanField(default=False)


class Profesor(models.Model):
    id = models.AutoField(primary_key=True)
    utilizator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class Disciplina(models.Model):
    id = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=100, unique=True)
    profesori = models.ManyToManyField(Profesor)
    an_universitar = models.IntegerField(null=True)
    semestru = models.IntegerField(null=True)


class Proiect(models.Model):
    id = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=100, unique=False)
    data_inregistrare = models.DateField(auto_now_add=True)
    data_intermediara = models.DateField(default=None)
    data_finalizare = models.DateField()
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE, null=True)
    document = models.CharField(max_length=100, null=True)
    nr_persoane = models.IntegerField(null=True)
    cale = models.CharField(max_length=100, default=None)
    distribuire_teme = models.BooleanField(default=False)


class Tema(models.Model):
    id = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=100, unique=False)
    descriere = models.CharField(max_length=500, null=True)
    proiect = models.ForeignKey(Proiect, on_delete=models.CASCADE, unique=False)


class Student(models.Model):
    id = models.AutoField(primary_key=True)
    utilizator = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    facultate = models.CharField(max_length=100, null=True)
    ciclu_de_studii = models.CharField(max_length=100, null=True)
    specializare = models.CharField(max_length=50, null=True)
    an_studiu = models.CharField(max_length=20, null=True)
    grupa = models.ForeignKey(Grupa, on_delete=models.CASCADE, null=True)
    teme = models.ManyToManyField(Tema)


class Incarcare(models.Model):
    id = models.AutoField(primary_key=True)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE)
    data_incarcare = models.DateField(null=True, unique=False)
    tip = models.CharField(max_length=20, null=True)
    document = models.CharField(max_length=100, null=True, unique=False)
    nota = models.FloatField(default=0)
    feedback = models.CharField(max_length=500, null=True)


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=100)
    descriere = models.CharField(max_length=300)
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, default=False)
    efectuat = models.BooleanField()


class DisciplinaProfesorStudent(models.Model):
    id = models.AutoField(primary_key=True)
    disciplina = models.ForeignKey(Disciplina, on_delete=models.CASCADE)
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)


class Echipa(models.Model):
    id = models.AutoField(primary_key=True)
    nume = models.CharField(max_length=100, null=True)
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE)
    proiect = models.ForeignKey(Proiect, on_delete=models.CASCADE, null=True)
    studenti = models.ManyToManyField(Student)

