from django.contrib import admin
from django.urls import path

from accounts import views as accounts_view


urlpatterns = [
    path('', accounts_view.home, name='home'),
    path('login/',accounts_view.loginPage, name='login'),
    path('register/',accounts_view.registerPage, name='register'),
]