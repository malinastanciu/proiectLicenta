from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from application.functions import create_context
from django.core.files.storage import FileSystemStorage
from application.models import Proiect, Disciplina


@login_required(login_url='login')
def dashboard(request):
    context = create_context(request)
    user_projects = Proiect.objects.all().filter(profesor=request.user)
    discipline = Disciplina.objects.all()
    context['projects'] = user_projects
    context['discipline'] = discipline
    return render(request, 'application/dashboard.html', context)


@login_required(login_url='login')
def account(request):
    context = create_context(request)
    return render(request, 'application/account.html', context)


@login_required(login_url='login')
def projects(request):
    context = create_context(request)
    project = Proiect()
    if request.method == 'POST':
        project.nume = request.POST.get('name')
        project.data_inregistare = date.today()
        project.data_finalizare = request.POST.get('final_date')
        project.profesor = request.user
        uploaded_file = request.FILES['document']
        project.cale = uploaded_file.name
        fs = FileSystemStorage()
        txt = uploaded_file.name
        x = txt.split('.')
        fs.save(project.nume + '.' + x[1], uploaded_file)
        project.save()
        return redirect('dashboard')
    return render(request, 'application/projects.html', context)


@login_required(login_url='login')
def adaugareDisciplina(request):
    context = create_context(request)
    disciplina = Disciplina()
    profesori = User.objects.filter(groups__name='profesori')
    print(profesori)
    if request.method == 'POST':
        disciplina.nume = request.POST.get('nume')
        disciplina.profesor = User.objects.filter(id=request.POST.get('profesor'))[0]
        disciplina.an_universitar = request.POST.get('an_universitar')
        disciplina.semestru = request.POST.get('semestru')
        disciplina.save()
        return redirect('dashboard')
    context['profesori'] = profesori
    return render(request, 'application/adaugare_disciplina.html', context)


@login_required(login_url='login')
def stergereDisciplina(request):
    context = create_context(request)
    discipline = Disciplina.objects.all()
    if request.method == 'POST':
        disciplina = Disciplina.objects.filter(id=request.POST.get('discipline'))[0]
        disciplina.delete()
        return redirect('dashboard')
    context['discipline'] = discipline
    return render(request, 'application/stergere disciplina.html', context)
