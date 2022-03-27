import ast
import datetime
import json
import os
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.exceptions import MultipleObjectsReturned
from django.shortcuts import render, redirect

import pandas
import numpy as np
import random

from django.utils.datastructures import MultiValueDictKeyError

from application.decorators import allowed_users
from application.functions import create_context
from django.core.files.storage import FileSystemStorage
from application.models import Proiect, Disciplina, Student, Grupa, Tema, Task, Incarcare, Profesor


@login_required(login_url='login')
def dashboard(request):
    context = create_context(request)
    discipline = Disciplina.objects.all()
    context['discipline'] = discipline
    print(discipline)
    print(request.user.groups.all())
    if 'studenti' == request.user.groups.all()[0].name:
        student = Student.objects.get(utilizator=request.user)
        context['student'] = student
        discipline_student = student.discipline.all()
        print(discipline_student)
        context['discipline_student'] = discipline_student
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
    disciplina = Disciplina.objects.get(pk=pk)
    context['disciplina'] = disciplina
    if request.method == 'POST':
        proiect.nume = request.POST.get('name')
        proiect.data_inregistrare = date.today()
        proiect.data_finalizare = request.POST.get('final_date')
        proiect.profesor = request.user
        proiect.disciplina = Disciplina.objects.get(pk=pk)
        proiect.nr_persoane = request.POST.get('nr_persoane')
        proiect.distribuire_teme = False

        path = os.path.abspath(os.getcwd()) + r"\media"
        path_of_directory = os.path.join(path, proiect.nume)
        os.mkdir(path_of_directory)
        try:
            uploaded_file = request.FILES['document']

            fs = FileSystemStorage(path_of_directory)
            txt = uploaded_file.name
            x = txt.split('.')
            fs.save(proiect.nume + '.' + x[1], uploaded_file)

            proiect.document = proiect.nume + '.' + x[1]
            proiect.cale = path_of_directory
            proiect.save()

            uploaded_file = request.FILES['document']
            file = pandas.ExcelFile(uploaded_file)
            for sheet in file.sheet_names:
                data = file.parse(sheet)
                dimensions = data.shape
                rows = dimensions[0]
                for i in range(0, rows):
                    teme = {}
                    tema = Tema()
                    for key in data.keys():
                        value = np.array(data.iloc[i][key]).tolist()
                        teme[key] = value
                    tema.nume = teme['Nume tema']
                    tema.descriere = teme['Descriere']
                    tema.proiect = proiect
                    tema.save()
        except MultiValueDictKeyError:
            proiect.cale = path_of_directory
            proiect.save()
        finally:
            return redirect('vizualizareDisciplina', pk=pk)
    return render(request, 'application/profesor/adaugare_proiect.html', context)


@allowed_users(allowed_roles=['admin'])
@login_required(login_url='login')
def adaugareDisciplina(request):
    context = create_context(request)
    profesori = Profesor.objects.all()
    disciplina = Disciplina()
    if request.method == 'POST':
        profesor = Profesor.objects.get(pk=request.POST.get('profesor'))
        try:
            disciplina_existenta = Disciplina.objects.get(nume=request.POST.get('nume'))
            disciplina_existenta.profesori.add(profesor)
            disciplina_existenta.save()
        except Disciplina.DoesNotExist:
            disciplina.nume = request.POST.get('nume')
            disciplina.an_universitar = request.POST.get('an_universitar')
            disciplina.semestru = request.POST.get('semestru')
            disciplina.save()
            disciplina.profesori.add(profesor)
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
    return render(request, 'application/secretariat/adaugare_studenti.html', context)


@allowed_users(allowed_roles=['secretariat'])
@login_required(login_url='login')
def vizualizareStudenti(request, pk):
    context = create_context(request)
    grupa = Grupa.objects.get(pk=pk)
    studenti = Student.objects.all().filter(grupa=grupa)
    context['studenti'] = studenti
    context['grupa'] = grupa
    return render(request, 'application/secretariat/vizualizare_studenti.html', context)


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
            profesor = Profesor()
            profesor.utilizator = utilizator_nou
            profesor.save()
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
    for disciplina in discipline:
        print(disciplina.profesori.all())
    context['discipline'] = discipline
    return render(request, 'application/administrator/vizualizareDiscipline.html', context)


@allowed_users(allowed_roles=['secretariat'])
@login_required(login_url='login')
def vizulalizareGrupe(request):
    context = create_context(request)
    grupe = Grupa.objects.all()
    context['grupe'] = grupe
    return render(request, 'application/secretariat/vizualizare_grupe.html', context)


@allowed_users(allowed_roles=['secretariat'])
@login_required(login_url='login')
def vizulalizareGrupeStudenti(request):
    context = create_context(request)
    grupe = Grupa.objects.all()
    context['grupe'] = grupe
    return render(request, 'application/secretariat/grupe_studenti.html', context)


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
    return render(request, 'application/secretariat/adaugare_grupa.html', context)


@allowed_users(allowed_roles=['secretariat'])
@login_required(login_url='login')
def asignareDiscipline(request, pk):
    context = create_context(request)
    grupa = Grupa.objects.get(pk=pk)
    discipline = Disciplina.objects.all().filter(an_universitar=int(grupa.nume[1]))
    grupa = Grupa.objects.get(pk=pk)
    studenti = Student.objects.all().filter(grupa=grupa)
    profesori = Profesor.objects.all()
    print(studenti)
    if request.method == 'POST':
        for disciplina in request.POST.getlist('disciplina'):
            dictionary = ast.literal_eval(disciplina)
            d = Disciplina.objects.get(pk=dictionary['disciplina'])
            p = Profesor.objects.get(pk=dictionary['profesor'])
            print(d)
            print(p)
            for student in studenti:
                student.discipline.add(d.id)
                student.profesori.add(p.id)
                student.save()
        return redirect('vizualizareGrupe')
    context['grupa'] = grupa
    context['discipline'] = discipline
    context['profesori'] = profesori
    return render(request, 'application/secretariat/asignare_discipline.html', context)


@allowed_users(allowed_roles=['profesori'])
@login_required(login_url='login')
def proiect(request, pk):
    proiect = Proiect.objects.get(pk=pk)
    teme = Tema.objects.all().filter(proiect=pk)
    context = create_context(request)
    context['proiect'] = proiect
    context['teme'] = teme
    return render(request, 'application/profesor/proiect.html', context)


@allowed_users(allowed_roles=['profesori'])
@login_required(login_url='login')
def distribuireTeme(request, pk):
    disciplina = Disciplina.objects.get(pk=pk)
    proiecte = Proiect.objects.all().filter(disciplina=disciplina)
    grupe = Grupa.objects.all()
    lista_teme = list()
    if request.method == 'POST':
        proiect = Proiect.objects.all().filter(id=request.POST.get('proiect'))
        print(proiect)
        teme = Tema.objects.all().filter(proiect=request.POST.get('proiect'))
        print(teme)
        for tema in teme:
            lista_teme.append(tema.id)
        print(lista_teme)
        grupa = Grupa.objects.all().filter(id=request.POST.get('grupa'))[0]
        # print(grupa.nume)
        studenti = Student.objects.all().filter(grupa=grupa)
        print(studenti)
        print(len(studenti))
        random.shuffle(lista_teme)
        print(lista_teme)
        for i in range(len(studenti)):
            print(studenti[i])
            # print(teme[i])
            tema = Tema.objects.get(id=lista_teme[i])
            print(tema)
            studenti[i].teme.add(tema)
        return redirect('vizualizareDisciplina', pk)
    context = create_context(request)
    context['disciplina'] = disciplina
    context['proiecte'] = proiecte
    context['grupe'] = grupe

    return render(request, 'application/profesor/distribuire_teme.html', context)


@allowed_users(allowed_roles=['studenti'])
@login_required(login_url='login')
def disciplinaStudent(request, pk):
    context = create_context(request)
    disciplina = Disciplina.objects.get(pk=pk)
    proiecte = Proiect.objects.all().filter(disciplina=disciplina)
    teme = Tema.objects.all().filter(proiect__in=proiecte)
    print(teme)
    student = Student.objects.get(utilizator=request.user)
    teme_student = student.teme.all().filter(proiect__in=proiecte)
    context['teme_student'] = teme_student
    if request.method == 'POST':
        return redirect('dashboard')
    context['disciplina'] = disciplina
    context['proiecte'] = proiecte
    return render(request, 'application/student/disciplinaStudent.html', context)


@allowed_users(allowed_roles=['studenti'])
@login_required(login_url='login')
def temaStudent(request, pk1):
    context = create_context(request)
    tema = Tema.objects.get(pk=pk1)
    proiect = Proiect.objects.get(tema=tema)
    print(proiect.nume)
    print(proiect.data_finalizare)
    print(date.today())
    if str(proiect.data_finalizare) > str(date.today()):
        context['data'] = True
    else:
        context['data'] = False

    tasks = Task.objects.all().filter(tema=tema)
    efectuat = 0
    for task in tasks:
        if task.efectuat == True:
            efectuat += 1
    if len(tasks) == 0:
        progresul = 0
    else:
        progresul = (100 / len(tasks)) * efectuat
    if request.method == 'POST':
        task = Task()
        task.nume = request.POST.get('nume')
        task.descriere = request.POST.get('descriere')
        task.tema = tema
        task.student = Student.objects.get(utilizator=request.user)
        task.efectuat = False
        task.save()
        efectuat = 0
        tasks_progres = Task.objects.all().filter(tema=tema)
        for task in tasks_progres:
            if task.efectuat == True:
                efectuat += 1
        progresul = 100 / len(tasks_progres) * efectuat
        context['progresul'] = progresul
        return redirect('temaStudent', pk1)
    context['tema'] = tema
    context['tasks'] = tasks
    context['progresul'] = progresul
    return render(request, 'application/student/tema.html', context)


@allowed_users(allowed_roles=['studenti'])
@login_required(login_url='login')
def efectuareTask(request, pk1, pk2):
    context = create_context(request)
    task = Task.objects.get(pk=pk2)
    if request.method == 'GET':
        task.efectuat = True
        task.save()
        return redirect('temaStudent', pk1)
    return render(request, 'application/student/tema.html', context)


@allowed_users(allowed_roles=['profesori'])
@login_required(login_url='login')
def vizualizareTema(request, pk):
    context = create_context(request)
    tema = Tema.objects.all().filter(id=pk).get(id=pk)
    # tema = Tema.objects.get(pk=pk)
    studenti = Student.objects.all().filter(teme=tema)
    tasks = Task.objects.all().filter(tema=tema)
    incarcari = Incarcare.objects.all().filter(tema=tema)
    print(incarcari)
    context['tema'] = tema
    context['studenti'] = studenti
    context['tasks'] = tasks
    context['incarcari'] = incarcari
    return render(request, 'application/profesor/vizualizareTema.html', context)


@allowed_users(allowed_roles=['studenti'])
@login_required(login_url='login')
def incarcareTema(request, pk):
    context = create_context(request)
    tema = Tema.objects.get(pk=pk)
    proiect = Proiect.objects.get(pk=tema.proiect.id)
    context['tema'] = tema
    context['proiect'] = proiect
    incarcare = Incarcare()
    if request.method == 'POST':
        path = os.path.abspath(os.getcwd()) + r"\media"
        print(path)
        print(date.today())
        print(Student.objects.get(utilizator=request.user))
        path_of_directory = os.path.join(path, proiect.nume)
        path_of_file = os.path.join(path_of_directory, request.user.first_name + '_' + request.user.last_name + '_' +
                                    tema.nume)
        os.mkdir(path_of_file)
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage(path_of_file)
        txt = uploaded_file.name
        x = txt.split('.')
        fs.save(request.user.first_name + '_' + request.user.last_name + '_' + tema.nume + '.' + x[1], uploaded_file)
        incarcare.tema = tema
        incarcare.data_incarcare = date.today()
        incarcare.student = Student.objects.get(utilizator=request.user.id)
        incarcare.document = request.user.first_name + '_' + request.user.last_name + '_' + tema.nume + '.' + x[1]
        incarcare.save()
        return redirect('temaStudent', tema.id)
    return render(request, 'application/student/incarcareTema.html', context)


@allowed_users(allowed_roles=['profesori'])
@login_required(login_url='login')
def adaugareNota(request, pk):
    context = create_context(request)
    tema = Tema.objects.get(pk=pk)
    incarcare = Incarcare.objects.get(tema=tema)
    print(incarcare.document)
    if request.method == 'POST':
        incarcare.nota = request.POST.get('nota')
        print(request.POST.get('nota'))
        incarcare.feedback = request.POST.get('feedback')
        incarcare.save()
        return redirect('vizualizareTema', pk)
    return render(request, 'application/profesor/vizualizareTema.html', context)


@allowed_users(allowed_roles=['secretariat'])
@login_required(login_url='login')
def modificareDiscipline(request, pk):
    context = create_context(request)
    print(pk)
    student = Student.objects.get(pk=pk)
    context['student'] = student
    grupa = Grupa.objects.get(pk=student.grupa.id)
    # context['student'] = stude
    discipline_student = student.discipline.all()
    for d in discipline_student:
        print(d.nume)
    context['discipline_student'] = discipline_student
    context['discipline'] = Disciplina.objects.all().filter(an_universitar=4)
    if request.method == 'POST':
        student.discipline.clear()
        for select in request.POST.getlist('select2'):
            dictionary = ast.literal_eval(select)
            profesor = User.objects.get(pk=dictionary['profesor'])
            disciplina = Disciplina.objects.all().filter(pk=dictionary['disciplina']).filter(profesori=profesor)
            disciplina = disciplina.get(profesori=profesor)
            print(profesor.last_name + ' ' + profesor.first_name)
            student.discipline.add(disciplina)
        return redirect('vizualizareStudenti', grupa.id)
    return render(request, 'application/secretariat/modificare_discipline.html', context)
