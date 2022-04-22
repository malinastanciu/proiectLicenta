import ast
import os
from io import StringIO, BytesIO
import xlsxwriter

from datetime import date
from openpyxl import Workbook

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.shortcuts import render, redirect

import pandas
import numpy as np
import random

from django.utils.datastructures import MultiValueDictKeyError
import mimetypes

from application.decorators import allowed_users
from application.functions import create_context
from django.core.files.storage import FileSystemStorage
from application.models import Proiect, Disciplina, Student, Grupa, Tema, Task, Incarcare, Profesor, \
    DisciplinaProfesorStudent, Echipa


@login_required(login_url='login')
def dashboard(request):
    context = create_context(request)
    if context['user_type'] == 'profesor':
        profesor = Profesor.objects.get(utilizator=request.user)
        discipline = Disciplina.objects.all().filter(profesori=profesor)
        context['discipline'] = discipline
    if 'studenti' == request.user.groups.all()[0].name:
        student = Student.objects.get(utilizator=request.user)
        context['student'] = student
        discipline_student = DisciplinaProfesorStudent.objects.all().filter(student=student)
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
        proiect.profesor = Profesor.objects.get(utilizator=request.user)
        proiect.disciplina = Disciplina.objects.get(pk=pk)
        proiect.nr_persoane = request.POST.get('nr_persoane')

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
    profesor = Profesor.objects.get(utilizator=request.user)
    proiecte = Proiect.objects.all().filter(profesor=profesor)
    proiecte = Proiect.objects.all().filter(profesor=profesor)
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
    if request.method == 'POST':
        for disciplina in request.POST.getlist('disciplina'):
            dictionary = ast.literal_eval(disciplina)
            d = Disciplina.objects.get(pk=dictionary['disciplina'])
            p = Profesor.objects.get(pk=dictionary['profesor'])
            for student in studenti:
                disciplina_profesor_student = DisciplinaProfesorStudent()
                disciplina_profesor_student.disciplina = d
                disciplina_profesor_student.profesor = p
                disciplina_profesor_student.student = student
                disciplina_profesor_student.save()
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
        proiect = Proiect.objects.get(id=request.POST.get('proiect'))
        teme = Tema.objects.all().filter(proiect=request.POST.get('proiect'))
        for tema in teme:
            lista_teme.append(tema.id)
        grupa = Grupa.objects.all().filter(id=request.POST.get('grupa'))[0]
        # print(grupa.nume)
        studenti = Student.objects.all().filter(grupa=grupa)
        random.shuffle(lista_teme)
        if len(lista_teme) >= len(studenti):
            if proiect.nr_persoane == 1:
                for i in range(len(studenti)):
                    tema = Tema.objects.get(id=lista_teme[i])
                    # studenti[i].teme.add(tema)
            else:
                j = 0
                lista_teme = lista_teme[:round(len(lista_teme) / proiect.nr_persoane)]
                for i in range(len(studenti)):
                    tema = Tema.objects.get(id=lista_teme[j])
                    # studenti[i].teme.add(tema)
                    j = j + 1
                    if j >= len(lista_teme):
                        j = 0
        else:
            if proiect.nr_persoane == 1:
                j = 0
                for i in range(len(studenti)):
                    tema = Tema.objects.get(id=lista_teme[j])
                    # studenti[i].teme.add(tema)
                    j = j + 1
                    if j >= len(lista_teme):
                        j = 0
            else:
                j = 0
                if len(lista_teme) > 5 * proiect.nr_persoane:
                    lista_teme = lista_teme[:round(len(lista_teme) / proiect.nr_persoane)]
                for i in range(len(studenti)):
                    tema = Tema.objects.get(id=lista_teme[j])
                    # studenti[i].teme.add(tema)
                    j = j + 1
                    if j >= len(lista_teme):
                        j = 0
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
    student = Student.objects.get(utilizator=request.user)
    teme_student = student.teme.all().filter(proiect__in=proiecte)
    print(teme_student)
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
    student = Student.objects.get(utilizator=request.user)
    if proiect.nr_persoane > 1:
        echipa = Echipa.objects.all().filter(tema=tema).filter(studenti=student)[0]
        context['echipa'] = echipa
    if str(proiect.data_finalizare) > str(date.today()):
        context['data'] = True
    else:
        context['data'] = False
    if proiect.nr_persoane == 1:
        tasks = Task.objects.all().filter(tema=tema)
    else:
        tasks = Task.objects.all().filter(tema=tema).filter(student__in=echipa.studenti.all())
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
    proiect = Proiect.objects.get(tema=tema)
    print(proiect.nr_persoane)
    # tema = Tema.objects.get(pk=pk)
    echipe = Echipa.objects.all().filter(proiect=proiect).filter(tema=tema)
    print(echipe)
    studenti = Student.objects.all().filter(teme=tema)
    incarcari = Incarcare.objects.all().filter(tema=tema)
    context['tema'] = tema
    context['studenti'] = studenti
    context['incarcari'] = incarcari
    context['proiect'] = proiect
    context['echipe'] = echipe
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
    student = Student.objects.get(pk=pk)
    nume_discipline = list()
    context['student'] = student
    grupa = Grupa.objects.get(pk=student.grupa.id)
    discipline_student = DisciplinaProfesorStudent.objects.all().filter(student=student)
    context['discipline_student'] = discipline_student
    context['discipline'] = Disciplina.objects.all().filter(an_universitar=4)
    if request.method == 'POST':
        materii = DisciplinaProfesorStudent.objects.all().filter(student=student)
        print(materii)
        materii.delete()
        for select in request.POST.getlist('select2'):
            print(select)
            document = DisciplinaProfesorStudent()
            dictionary = ast.literal_eval(select)
            profesor = Profesor.objects.get(pk=dictionary['profesor'])
            print(profesor)
            disciplina = Disciplina.objects.get(pk=dictionary['disciplina'])
            print(disciplina)

            document.disciplina = disciplina
            document.student = student
            document.profesor = profesor
            document.save()
        return redirect('vizualizareStudenti', grupa.id)
    return render(request, 'application/secretariat/modificare_discipline.html', context)


@allowed_users(allowed_roles=['profesori'])
@login_required(login_url='login')
def adaugareTema(request, pk):
    proiect = Proiect.objects.get(pk=pk)
    if request.method == 'POST':
        tema = Tema()
        tema.nume = request.POST.get('nume')
        tema.descriere = request.POST.get('descriere')
        tema.proiect = proiect
        tema.save()
        return redirect('proiect', pk)


@allowed_users(allowed_roles=['profesori'])
@login_required(login_url='login')
def creareEchipe(request, pk):
    context = create_context(request)
    tema = Tema.objects.get(pk=pk)
    studenti = Student.objects.all().filter(teme=tema)
    context['tema'] = tema
    context['studenti'] = studenti
    proiect = Proiect.objects.get(tema=tema)
    context['proiect'] = proiect
    echipe = Echipa.objects.all().filter(tema=tema)
    studenti_cu_echipa = list()
    for echipa in echipe:
        for student in echipa.studenti.all():
            studenti_cu_echipa.append(student)
    context['studenti_cu_echipa'] = studenti_cu_echipa
    print(studenti_cu_echipa)
    if request.method == 'POST':
        echipa = Echipa()
        echipa.nume = request.POST.get('nume')
        echipa.tema = tema
        echipa.proiect = proiect
        echipa.save()
        for select in request.POST.getlist('select2'):
            student = Student.objects.get(id=select)
            grupa = student.grupa
            echipa.studenti.add(student)
            echipa.save()
        echipa.grupa = grupa
        echipa.save()
        return redirect('vizualizareTema', tema.id)
    return render(request, 'application/profesor/creare_echipe.html', context)


@allowed_users(allowed_roles=['profesori'])
@login_required(login_url='login')
def catalog(request, pk):
    context = create_context(request)

    profesor = Profesor.objects.get(utilizator=request.user)
    disciplina = Disciplina.objects.get(pk=pk)
    studenti = DisciplinaProfesorStudent.objects.all().filter(profesor=profesor)
    lista_grupe = list()
    for student in studenti:
        if student.student.grupa.nume not in lista_grupe:
            lista_grupe.append(student.student.grupa.nume)
    print(lista_grupe)
    grupe = Grupa.objects.all().filter(nume__in=lista_grupe)
    context['grupe'] = grupe
    context['disciplina'] = disciplina
    context['action'] = 'Vizualizare grupe'
    return render(request, 'application/profesor/catalog.html', context)


@allowed_users(allowed_roles=['profesori'])
@login_required(login_url='login')
def vizualizareCatalog(request, pk1, pk2):
    context = create_context(request)
    disciplina = Disciplina.objects.get(pk=pk1)
    proiecte = Proiect.objects.all().filter(disciplina=disciplina)
    grupa = Grupa.objects.get(pk=pk2)
    studenti = Student.objects.all().filter(grupa=grupa)
    incarcari = Incarcare.objects.all()
    context['action'] = 'Vizualizare catalog grupa'
    context['grupa'] = grupa
    lista_teme = list()
    for student in studenti:
        lista_teme.append(student.teme.all().filter(proiect__in=proiecte))
        nr_teme = len(student.teme.all().filter(proiect__in=proiecte))
    lista_nr_teme = list()
    for i in range(nr_teme):
        lista_nr_teme.append(i)
    context['studenti'] = studenti
    context['proiecte'] = proiecte
    context['disciplina'] = disciplina
    context['incarcari'] = incarcari
    context['lista_teme'] = lista_teme
    context['lista_nr_teme'] = lista_nr_teme
    context['nr_teme'] = nr_teme
    context['nr_teme2'] = range(nr_teme)
    return render(request, 'application/profesor/catalog.html', context)


@allowed_users(allowed_roles=['studenti'])
@login_required(login_url='login')
def note(request, pk):
    context = create_context(request)
    student = Student.objects.get(utilizator=request.user)
    disciplina = Disciplina.objects.get(pk=pk)
    proiecte = Proiect.objects.all().filter(disciplina=disciplina)
    teme = Tema.objects.all().filter(proiect__in=proiecte).filter(id__in=student.teme.all())
    incarcari = Incarcare.objects.all().filter(student=student)
    context['student'] = student
    context['disciplina'] = disciplina
    context['teme'] = teme
    context['proiecte'] = proiecte
    context['incarcari'] = incarcari
    return render(request, 'application/student/note.html', context)


@allowed_users(allowed_roles=['profesori'])
@login_required(login_url='login')
def download(request, pk1, pk2):
    tema = Tema.objects.get(pk=pk1)
    proiect = Proiect.objects.get(tema=tema)
    incarcare = Incarcare.objects.get(pk=pk2)
    path = os.path.abspath(os.getcwd()) + r"\media"
    path_of_directory = os.path.join(path, proiect.nume)
    print(path_of_directory)
    path_of_file = os.path.join(path_of_directory, incarcare.student.utilizator.first_name + '_' +
                                incarcare.student.utilizator.last_name + '_' + tema.nume)
    path_of_file = os.path.join(path_of_file, incarcare.document)
    path = open(path_of_file, 'rb')
    mime_type, _ = mimetypes.guess_type(path_of_file)
    response = HttpResponse(path, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % incarcare.document
    return response


@allowed_users(allowed_roles=['profesori'])
@login_required(login_url='login')
def descarcareCatalog(request, pk1, pk2):
    context = create_context(request)
    disciplina = Disciplina.objects.get(pk=pk1)
    proiecte = Proiect.objects.all().filter(disciplina=disciplina)
    grupa = Grupa.objects.get(pk=pk2)
    studenti = Student.objects.all().filter(grupa=grupa)
    incarcari = Incarcare.objects.all()
    context['studenti'] = studenti
    context['proiecte'] = proiecte
    context['disciplina'] = disciplina
    context['incarcari'] = incarcari
    nr_teme = len(studenti[0].teme.all().filter(proiect__in=proiecte))
    print(nr_teme)
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    header = workbook.add_format({
        'color': 'black',
        'bold': True,
        'align': 'left',
        'valign': 'top',
        'border': 1
    })
    worksheet.set_column(0, 8, width=20)
    worksheet.write(0, 0, 'Surname', header)
    worksheet.write(0, 1, 'First name', header)
    worksheet.write(0, 2, 'Email address', header)
    worksheet.write(0, 3, 'An Universitar', header)
    worksheet.write(0, 4, 'Facultatea', header)
    worksheet.write(0, 5, 'Ciclu de studii', header)
    worksheet.write(0, 6, 'Specializarea', header)
    worksheet.write(0, 7, 'Anul', header)
    worksheet.write(0, 8, 'Grupa', header)
    for i in range(nr_teme):
        worksheet.write(0, 9 + i, 'Punctaj ' + str(i + 1), header)
    for idx, student in enumerate(studenti):
        row = 1 + idx
        worksheet.write_string(row, 0, student.utilizator.last_name)
        worksheet.write_string(row, 1, student.utilizator.first_name)
        worksheet.write_string(row, 2, student.utilizator.email)
        worksheet.write_string(row, 3, str(date.today().year))
        worksheet.write_string(row, 4, student.facultate)
        worksheet.write_string(row, 5, student.ciclu_de_studii)
        worksheet.write_string(row, 6, student.specializare)
        worksheet.write_string(row, 7, student.an_studiu)
        worksheet.write_string(row, 8, student.grupa.nume)
        for idx2, tema in enumerate(student.teme.all().filter(proiect__in=proiecte)):
            incarcare = incarcari.filter(tema=tema).filter(student=student).first()
            try:
                worksheet.write_number(row, 9 + idx2, incarcare.nota)
            except AttributeError:
                worksheet.write_number(row, 9 + idx2, 0)
    workbook.close()
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # tell the browser what the file is named
    excel_nume = 'Catalog ' + disciplina.nume + ' grupa ' + grupa.nume
    response['Content-Disposition'] = "attachment;filename=%s" % excel_nume
    # put the spreadsheet data into the response
    response.write(output.getvalue())
    # return the response
    return response
