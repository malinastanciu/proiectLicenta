from django.contrib.auth.models import User
from accounts.forms import CreateUserForm, UserCreationForm
from django.urls import reverse
from django.urls import resolve
from django.test import TestCase
from accounts.views import loginPage, registerPage


class SignInFormTest(TestCase):
    def test_form_has_fields(self):
        form = CreateUserForm()
        expected = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)

    def test_form_has_not_fields(self):
        form = UserCreationForm()
        expected = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']
        actual = list(form.fields)
        self.assertNotEqual(expected, actual)

    def setUp(self):
        url = reverse('login')
        self.response = self.client.get(url)

    def test_signup_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        view = resolve('/conectare/')
        self.assertEquals(view.func, loginPage)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')


class SignUpFormTest(TestCase):

    def setUp(self):
        url = reverse('register')
        self.response = self.client.get(url)

    def test_signup_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        view = resolve('/creare_cont/')
        self.assertEquals(view.func, registerPage)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('user')
        self.assertIsInstance(form, CreateUserForm)


class SuccessfulSignUpTests(TestCase):
    def setUp(self):
        url = reverse('register')
        data = {
            'username': 'john',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456'
        }
        self.response = self.client.post(url, data)
        self.home_url = reverse('login')

    def test_redirection(self):
        '''
        A valid form submission should redirect the user to the home page
        '''
        self.assertRedirects(self.response, self.home_url)


class InvalidSignUpTests(TestCase):
    def setUp(self):
        url = reverse('register')
        self.response = self.client.post(url, {})  # submit an empty dictionary

    def test_signup_status_code(self):
        '''
        An invalid form submission should return to the same page
        '''
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context.get('user')
        self.assertTrue(form.errors)

    def test_dont_create_user(self):
        self.assertFalse(User.objects.exists())


USER_DATA = {
    'username': 'john',
    'email': 'john@gmail.com',
    'password1': 'abcdef123456',
    'password2': 'abcdef123456',
    'first_name': 'John',
    'last_name': 'John'}


class AccountValidRoutesTests(TestCase):
    def setUp(self):

        self.data = USER_DATA
        user = User.objects.create_user(username=self.data['username'],
                                        email=self.data['email'],
                                        password=self.data['password1'],
                                        first_name=self.data['first_name'],
                                        last_name=self.data['last_name'])

        # Logging in the app
        login_url = reverse('login')
        login_data = {
            'username': self.data['username'],
            'password': self.data['password1']
        }
        self.client.post(login_url, login_data)

    def test_password_change_view_success_status_code(self):
        url = reverse('change_password')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_password_change_done_view_success_status_code(self):
        url = reverse('password_change_done')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)




