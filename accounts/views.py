from django.contrib.auth import logout, login, authenticate
from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.forms import UserCreationForm
from accounts.forms import CreateUserForm


def home(request):
    return HttpResponse('Hello world!')


def loginPage(request):
    if request.method =='POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
    context = {'page_name': 'Login'}
    return render(request, 'accounts/login.html', context)


def registerPage(request):
    user = CreateUserForm()
    if request.method == 'POST':
        user = CreateUserForm(request.POST)
        if user.is_valid():
            user.save()
            return redirect('login')
    context = {'user': user, 'page_name': 'Register'}
    return render(request, 'accounts/register.html', context)


def logoutPage(request):
    logout(request)
    return redirect('login')
