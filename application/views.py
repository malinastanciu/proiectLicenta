from datetime import date

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from application.functions import create_context
from django.core.files.storage import FileSystemStorage
from application.models import Project


@login_required(login_url='login')
def dashboard(request):
    context = create_context(request)
    user_projects = Project.objects.all().filter(ownerID=request.user)
    context['projects'] = user_projects
    return render(request, 'application/dashboard.html', context)


@login_required(login_url='login')
def account(request):
    context = create_context(request)
    return render(request, 'application/account.html', context)


@login_required(login_url='login')
def projects(request):
    context = create_context(request)
    project = Project()
    if request.method == 'POST':
        project.name = request.POST.get('name')
        project.registration_date = date.today()
        project.final_date = request.POST.get('final_date')
        project.ownerID = request.user
        uploaded_file = request.FILES['document']
        project.path = uploaded_file.name
        fs = FileSystemStorage()
        txt = uploaded_file.name
        x = txt.split('.')
        fs.save(project.name + '.'+x[1], uploaded_file)
        project.save()
        return redirect('dashboard')
    return render(request, 'application/projects.html', context)
