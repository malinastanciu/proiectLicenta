from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from accounts import views as accounts_view


urlpatterns = [
    path('login/', accounts_view.loginPage, name='login'),
    path('register/', accounts_view.registerPage, name='register'),
    path('logout/', accounts_view.logoutPage, name='logout'),
    path('reset_password/',
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'),
         name="reset_password"),
    path('reset_password_sent/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_sent.html'),
         name="password_reset_done"),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name="password_reset_confirm"),
    path('reset_password_complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name="password_reset_complete"),
]