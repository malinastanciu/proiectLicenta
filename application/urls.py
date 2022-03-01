from django.contrib import admin
from django.urls import path

from application import views as application_views


urlpatterns = [
    path('', application_views.dashboard, name='dashboard'),
    path('cont/', application_views.account, name='account'),
    path('adaugare-proiect-nou/', application_views.projects, name='projects'),
    path('adaugare-disciplina-noua/', application_views.adaugareDisciplina, name='adaugareDisciplina'),

]