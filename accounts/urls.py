from django.contrib import admin
from django.urls import path

from accounts import views as accounts_view


urlpatterns = [
    path('', accounts_view.home, name='home'),
]