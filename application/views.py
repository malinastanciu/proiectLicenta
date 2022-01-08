from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from application.functions import create_context


@login_required(login_url='login')
def dashboard(request):
    context = create_context(request)
    return render(request, 'application/dashboard.html', context)


@login_required(login_url='login')
def account(request):
    context = create_context(request)
    return render(request, 'application/account.html', context)


@login_required(login_url='login')
def projects(request):
    context = create_context(request)
    return render(request, 'application/projects.html', context)
