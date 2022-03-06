from django.contrib import messages
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from accounts.forms import CreateUserForm
from application.decorators import allowed_users


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.info(request, 'Numele de utilizator sau parola sunt incorecte')
    context = {}
    return render(request, 'accounts/login.html', context)


def registerPage(request):
    user = CreateUserForm()
    if request.method == 'POST':
        user = CreateUserForm(request.POST)
        if user.is_valid():
            user = user.save(commit=False)
            if user.email.endswith('@upb.ro'):
                user.save()
                group = Group.objects.get(name='profesori')
                user.groups.add(group)
            # elif user.email.endswith('@stud.acs.upb.ro'):
            #     user.save()
            #     group = Group.objects.get(name='studenti')
            #     user.groups.add(group)
            return redirect('login')
    context = {'user': user, 'page_name': 'Creare cont'}
    return render(request, 'accounts/register.html', context)


def logoutPage(request):
    logout(request)
    return redirect('login')
