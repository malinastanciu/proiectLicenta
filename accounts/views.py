from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def home(request):
    return HttpResponse('Hello world!')


def loginPage(request):
    form = UserCreationForm()
    context = {'form': form}
    return render(request, 'accounts/login.html', context)

def registerPage(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    context = {'form': form}
    return render(request, 'accounts/register.html', context)
