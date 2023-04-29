from django.urls import reverse
from django.urls import resolve
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from application.views import adaugareGrupa

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

    def test_stergere_disciplina_view(self):
        view = resolve('/stergere-disciplina-existenta/')
        self.assertEquals(view.func, stergereDisciplina)

    def test_stergere_disciplina_view_success_status_code(self):
        url = reverse('stergereDisciplina')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_adaugare_cont_view(self):
        view = resolve('/adaugare-cont-utilizator/')
        self.assertEquals(view.func, adaugareCont)

    def test_adaugare_cont_view_success_status_code(self):
        url = reverse('adaugareCont')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_stergere_cont_view(self):
        view = resolve('/stergere-cont-utilizator/')
        self.assertEquals(view.func, stergereCont)

    def test_stergere_cont_view_success_status_code(self):
        url = reverse('stergereCont')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_vizualizare_discipline_view(self):
        view = resolve('/vizualizare-discipline/')
        self.assertEquals(view.func, vizualizareDiscipline)

    def test_vizualizare_discipline_view_success_status_code(self):
        url = reverse('vizualizareDiscipline')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
