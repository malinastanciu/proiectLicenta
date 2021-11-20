from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.forms import UserCreationForm
from accounts.forms import CreateUserForm


# Create your views here.
def home(request):
    return HttpResponse('Hello world!')


def loginPage(request):
    form = UserCreationForm()
    context = {'form': form,'page_name':'Login'}
    return render(request, 'accounts/login.html', context)

def registerPage(request):
    form = CreateUserForm()
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    context = {'form': form,'page_name':'Register'}
    return render(request, 'accounts/register.html', context)
