from django.urls import reverse
from django.urls import resolve
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from application.models import Grupa, Profesor, Student
from application.views import adaugareGrupa, adaugareStudenti, vizulalizareGrupe, asignareDiscipline, \
    vizulalizareGrupeStudenti, vizualizareStudenti

User = get_user_model()
USER_DATA = {
    'username': 'john',
    'email': 'john@gmail.com',
    'password1': 'abcdef123456',
    'password2': 'abcdef123456',
    'first_name': 'John',
    'last_name': 'John'
}


class SecretariatValidRoutesTests(TestCase):
    def setUp(self):
        self.data = USER_DATA

        user = User.objects.create_user(username=self.data['username'],
                                        email=self.data['email'],
                                        password=self.data['password1'],
                                        first_name=self.data['first_name'],
                                        last_name=self.data['last_name'])

        user_group = Group.objects.create(name='secretariat')
        user.groups.add(user_group)
        Group.objects.create(name='studenti')
        User.objects.create_user(username='maria',
                                 email='maria@upb.ro',
                                 password='maria',
                                 first_name='Maria',
                                 last_name='Ionescu')
        at_user_profesor = User.objects.get(email='maria@upb.ro')
        self.grupa = Grupa()
        self.grupa.nume = "331AC"
        self.grupa.asignare_discipline = False
        self.grupa.save()

        self.profesor = Profesor()
        self.profesor.utilizator = at_user_profesor
        self.profesor.save()
        self.grupa.asignare_discipline = False
        self.grupa.save()

        # Logging in the app
        login_url = reverse('login')
        login_data = {
            'username': self.data['username'],
            'password': self.data['password1']
        }
        self.client.post(login_url, login_data)

    def test_adaugare_grupa_view(self):
        view = resolve('/adaugare-grupa/')
        self.assertEquals(view.func, adaugareGrupa)

    def test_adaugare_grupa_view_success_status_code(self):
        url = reverse('adaugareGrupa')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_adaugare_studenti_view(self):
        view = resolve('/adaugare-studenti/')
        self.assertEquals(view.func, adaugareStudenti)

    def test_adaugare_studenti_view_success_status_code(self):
        url = reverse('adaugareStudenti')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_vizualizare_grupe_view(self):
        view = resolve('/vizualizare-grupe/')
        self.assertEquals(view.func, vizulalizareGrupe)

    def test_vizualizare_grupe_view_success_status_code(self):
        url = reverse('vizualizareGrupe')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_asignare_discipline_view(self):
        view = resolve('/vizualizare-grupe/asignare-discipline/' + str(self.grupa.id))
        self.assertEquals(view.func, asignareDiscipline)

    def test_asignare_discipline_view_success_status_code(self):
        self.client.post(reverse('vizualizareGrupe'))
        url = reverse('asignareDiscipline', kwargs={'pk': self.grupa.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_vizualizare_studenti_view(self):
        view = resolve('/vizualizare-grupe-studenti/')
        self.assertEquals(view.func, vizulalizareGrupeStudenti)

    def test_vizualizare_studenti_view_success_status_code(self):
        url = reverse('vizualizareGrupeStudenti')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_vizualizare_studenti_grupa_view(self):
        view = resolve('/vizualizare-studenti/grupa/' + str(self.grupa.id))
        self.assertEquals(view.func, vizualizareStudenti)

    def test_vizualizare_studenti_grupa_view_success_status_code(self):
        url = reverse('vizualizareStudenti', kwargs={'pk': self.grupa.id})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)


