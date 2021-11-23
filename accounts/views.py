from django.contrib import messages
from django.contrib.auth import logout, login, authenticate, get_user_model
from django.contrib.auth.models import Group,User
from django.shortcuts import render, HttpResponse, redirect
from accounts.forms import CreateUserForm
# User = get_user_model()


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.info(request, 'Username or password is incorrect')
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
                group = Group.objects.get(name='teachers')
                user.groups.add(group)
            elif user.email.endswith('@stud.acs.upb.ro'):
                user.save()
                group = Group.objects.get(name='students')
                user.groups.add(group)
            return redirect('login')
    context = {'user': user, 'page_name': 'Register'}
    return render(request, 'accounts/register.html', context)


def logoutPage(request):
    logout(request)
    return redirect('login')
