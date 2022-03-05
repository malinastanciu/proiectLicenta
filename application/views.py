from datetime import date
from turtle import pd

import openpyxl
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect
from openpyxl import load_workbook
import pandas
import numpy as np

from accounts.forms import CreateUserForm
from application.decorators import allowed_users
from application.functions import create_context
from django.core.files.storage import FileSystemStorage
from application.models import Proiect, Disciplina, Student


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


@allowed_users(allowed_roles=['profesori'])
@login_required(login_url='login')
def adaugareProiect(request, pk):
    context = create_context(request)
    proiect = Proiect()
    if request.method == 'POST':
        proiect.nume = request.POST.get('name')
        proiect.data_inregistrare = date.today()
        proiect.data_finalizare = request.POST.get('final_date')
        proiect.profesor = request.user
        proiect.disciplina = Disciplina.objects.get(pk=pk)
        uploaded_file = request.FILES['document']
        proiect.document = uploaded_file.name
        fs = FileSystemStorage()
        txt = uploaded_file.name
        x = txt.split('.')
        fs.save(proiect.nume + '.' + x[1], uploaded_file)
        proiect.cale = proiect.nume + '.' + x[1]
        proiect.save()
        return redirect('vizualizareDisciplina', pk=pk)
    return render(request, 'application/adaugare_proiect.html', context)


@allowed_users(allowed_roles=['admin'])
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


@allowed_users(allowed_roles=['admin'])
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


@allowed_users(allowed_roles=['profesori'])
@login_required(login_url='login')
def vizualizareDisciplina(request, pk):
    context = create_context(request)
    disciplina = Disciplina.objects.get(pk=pk)
    if request.method == 'POST':
        return redirect('dashboard')
    context['disciplina'] = disciplina
    return render(request, 'application/vizualizare_disciplina.html', context)


@allowed_users(allowed_roles=['profesori'])
@login_required(login_url='login')
def vizualizareProiecte(request, pk):
    context = create_context(request)
    proiecte = Proiect.objects.all()
    disciplina = Disciplina.objects.get(pk=pk)
    if request.method == 'POST':
        return redirect('vizualizareDisciplina')
    context['proiecte'] = proiecte
    context['disciplina'] = disciplina
    return render(request, 'application/vizualizare_proiecte.html', context)


@allowed_users(allowed_roles=['admin'])
@login_required(login_url='login')
def adaugareStudenti(request):
    context = create_context(request)
    group = Group.objects.get(name='studenti')
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        # workbook = load_workbook(filename=uploaded_file)
        file = pandas.ExcelFile(uploaded_file)
        for sheet in file.sheet_names:
            data = file.parse(sheet)
            dimensions = data.shape
            rows = dimensions[0]
            # columns = dimensions[1]
            for i in range(0, rows):
                student = {}
                for key in data.keys():
                    value = np.array(data.iloc[i][key]).tolist()
                    student[key] = value
                email = str(student['Email address'])
                user = User.objects.create_user(username=email.split('@')[0], email=email, password='student123456',
                                                first_name=student['First name'], last_name=student['Surname'])

                group.user_set.add(user)
                utilizator = User.objects.get(email=email)
                stud = Student()
                stud.utilizator = utilizator
                stud.facultate = student['Facultatea']
                stud.ciclu_de_studii = student['Ciclu de studii']
                stud.specializare = student['Specializarea']
                stud.an_studiu = student['Anul']
                stud.grupa = student['Grupa']
                stud.save()
        return redirect('dashboard')
    return render(request, 'application/adaugare_studenti.html', context)
