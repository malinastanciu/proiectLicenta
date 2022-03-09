from django.contrib import admin
from django.urls import path

from application import views as application_views

urlpatterns = [
    path('', application_views.dashboard, name='dashboard'),
    path('cont/', application_views.account, name='account'),
    path('adaugare-disciplina-noua/', application_views.adaugareDisciplina, name='adaugareDisciplina'),
    path('stergere-disciplina-existenta/', application_views.stergereDisciplina, name='stergereDisciplina'),
    path('vizualizare-disciplina/<str:pk>', application_views.vizualizareDisciplina, name='vizualizareDisciplina'),
    path('vizualizare-disciplina/<str:pk>/adaugare-proiect-nou/', application_views.adaugareProiect,
         name='adaugareProiect'),
    path('vizualizare-disciplina/<str:pk>/vizualizare-proiecte/', application_views.vizualizareProiecte,
         name='vizualizareProiecte'),
    path('adugare-studenti/', application_views.adaugareStudenti, name='adaugareStudenti'),
    path('vizualizare-studenti/', application_views.vizualizareStudenti, name='vizualizareStudenti'),
    path('stergere-cont-utilizator/', application_views.stergereCont, name='stergereCont'),
    path('adaugare-cont-utilizator/', application_views.adaugareCont, name='adaugareCont'),
    path('vizualizare-discipline/', application_views.vizualizareDiscipline, name='vizualizareDiscipline'),
    path('asignare-discipline/', application_views.asignareDiscipline, name='asignareDiscipline'),
    path('adaugare-grupa/', application_views.adaugareGrupa, name='adaugareGrupa'),
]
