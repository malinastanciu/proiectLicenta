from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.shortcuts import render, redirect

import pandas
import numpy as np

from application.decorators import allowed_users
from application.functions import create_context
from django.core.files.storage import FileSystemStorage
from application.models import Proiect, Disciplina, Student, Grupa


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
    return render(request, 'application/profesor/adaugare_proiect.html', context)


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
    return render(request, 'application/administrator/adaugare_disciplina.html', context)


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
    return render(request, 'application/administrator/stergere disciplina.html', context)


@allowed_users(allowed_roles=['profesori'])
@login_required(login_url='login')
def vizualizareDisciplina(request, pk):
    context = create_context(request)
    disciplina = Disciplina.objects.get(pk=pk)
    if request.method == 'POST':
        return redirect('dashboard')
    context['disciplina'] = disciplina
    return render(request, 'application/profesor/vizualizare_disciplina.html', context)


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
    return render(request, 'application/profesor/vizualizare_proiecte.html', context)


@allowed_users(allowed_roles=['secretariat'])
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
                if i == 0:
                    grupa = Grupa.objects.filter(nume=student['Grupa'])[0]
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
                stud.grupa = grupa
                stud.save()

        return redirect('dashboard')
    return render(request, 'application/scretariat/adaugare_studenti.html', context)


@allowed_users(allowed_roles=['secretariat'])
@login_required(login_url='login')
def vizualizareStudenti(request):
    context = create_context(request)
    studenti = Student.objects.all()
    context['studenti'] = studenti
    return render(request, 'application/scretariat/vizualizare_studenti.html', context)


@allowed_users(allowed_roles=['admin'])
@login_required(login_url='login')
def stergereCont(request):
    context = create_context(request)
    utilizatori = User.objects.filter(groups__name='studenti')
    profesori = User.objects.filter(groups__name='profesori')
    if request.method == 'POST':
        utilizator = User.objects.filter(id=request.POST.get('utilizator'))[0]
        utilizator.delete()
        return redirect('dashboard')
    context['utilizatori'] = utilizatori
    context['profesori'] = profesori
    return render(request, 'application/administrator/stergere_cont.html', context)


@allowed_users(allowed_roles=['admin'])
@login_required(login_url='login')
def adaugareCont(request):
    context = create_context(request)
    if request.method == 'POST':
        email = request.POST.get('email')
        if request.POST.get('tip') == 'student':
            utilizator_nou = User.objects.create_user(username=email.split('@')[0], email=email,
                                                      password='student123456', first_name=request.POST.get('prenume'),
                                                      last_name=request.POST.get('nume'))
            group = Group.objects.get(name='studenti')
            utilizator_nou.groups.add(group)
        elif request.POST.get('tip') == 'profesor':
            utilizator_nou = User.objects.create_user(username=email.split('@')[0], email=email,
                                                      password='profesor123456', first_name=request.POST.get('prenume'),
                                                      last_name=request.POST.get('nume'))
            group = Group.objects.get(name='profesori')
            utilizator_nou.groups.add(group)
        elif request.POST.get('tip') == 'secretar':
            utilizator_nou = User.objects.create_user(username=email.split('@')[0], email=email,
                                                      password='secretar123456', first_name=request.POST.get('prenume'),
                                                      last_name=request.POST.get('nume'))
            group = Group.objects.get(name='secretariat')
            utilizator_nou.groups.add(group)
        return redirect('dashboard')
    return render(request, 'application/administrator/adaugare_cont.html', context)


@allowed_users(allowed_roles=['admin'])
@login_required(login_url='login')
def vizualizareDiscipline(request):
    context = create_context(request)
    discipline = Disciplina.objects.all()
    context['discipline'] = discipline
    return render(request, 'application/administrator/vizualizareDiscipline.html', context)


@allowed_users(allowed_roles=['secretariat'])
@login_required(login_url='login')
def asignareDiscipline(request):
    context = create_context(request)
    discipline = Disciplina.objects.all()
    context['discipline'] = discipline
    return render(request, 'application/scretariat/asignarea_disciplinelor.html', context)


@allowed_users(allowed_roles=['secretariat'])
@login_required(login_url='login')
def adaugareGrupa(request):
    context = create_context(request)
    grupe = Grupa.objects.all()
    grupa = Grupa()
    if request.method == 'POST':
        grupa.nume = request.POST.get('nume')
        grupa.save()
        return redirect('adaugareGrupa')
    context['grupe'] = grupe
    return render(request, 'application/scretariat/adaugare_grupa.html', context)
