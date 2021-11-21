from django.contrib import admin
from django.urls import path

from application import views as application_views


urlpatterns = [
    path('', application_views.dashboard, name='dashboard'),

]