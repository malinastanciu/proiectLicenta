from django.db import models
from django.contrib.auth.models import Group, User


# Create your models here.
class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    registration_date = models.DateField(auto_now_add=True)
    final_date = models.DateField()
    ownerID = models.ForeignKey(User, on_delete=models.CASCADE)


class PathProject(models.Model):
    id = models.AutoField(primary_key=True)
    path = models.CharField(max_length=100)


class Assignments(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    projectID = models.ForeignKey(Project, on_delete=models.CASCADE)
    studentID = models.ForeignKey(User, on_delete=models.CASCADE)
    path = models.ForeignKey(PathProject, on_delete=models.CASCADE)
