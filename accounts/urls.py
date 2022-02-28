from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from accounts import views as accounts_view


urlpatterns = [
    path('conectare/', accounts_view.loginPage, name='login'),
    path('creare_cont/', accounts_view.registerPage, name='register'),
    path('deconectare/', accounts_view.logoutPage, name='logout'),
    path('resetare-parola/',
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'),
         name="reset_password"),
    path('resetare-parola-trimisa/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_sent.html'),
         name="password_reset_done"),
    path('resetare-parola/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name="password_reset_confirm"),
    path('resetare-parola-completa/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name="password_reset_complete"),
    path('cont/schimbare-parola/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/change_password.html'),
         name='change_password'),
    path('cont/schimbare-parola-completa/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/change_password_done.html'),
         name='password_change_done'),
]