from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.forms import UserCreationForm
from accounts.forms import CreateUserForm



# Create your views here.
def home(request):
    return HttpResponse('Hello world!')


def loginPage(request):
    form = UserCreationForm()
    context = {'form': form, 'page_name': 'Login'}
    return render(request, 'accounts/login.html', context)


def registerPage(request):
    user = CreateUserForm()
    if request.method == 'POST':
        user = CreateUserForm(request.POST)
        user.username = request.POST
        if user.is_valid():
            user.save()
            return redirect('login')
    context = {'user': user, 'page_name': 'Register'}
    return render(request, 'accounts/register.html', context)
