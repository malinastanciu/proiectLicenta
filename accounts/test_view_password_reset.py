from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.urls import reverse
from django.urls import resolve
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

User = get_user_model()
USER_DATA = {
    'username': 'john',
    'email': 'john@gmail.com',
    'password1': 'abcdef123456',
    'password2': 'abcdef123456',
    'first_name': 'John',
    'last_name': 'John'
}


class PasswordResetTests(TestCase):
    def setUp(self):
        url = reverse('reset_password')
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/resetare-parola/')
        self.assertEquals(view.func.view_class, auth_views.PasswordResetView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PasswordResetForm)

    def test_form_inputs(self):
        '''
        The view must contain two inputs: csrf and email
        '''
        self.assertContains(self.response, '<input', 4)
        self.assertContains(self.response, 'type="email"', 1)


class SuccessfulPasswordResetTests(TestCase):
    def setUp(self):
        url = reverse('register')
        self.data = {
            'username': 'john',
            'email': 'john@gmail.com',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456',
            'first_name': 'John',
            'last_name': 'John'
        }
        Group.objects.create(name="studenti")
        self.response = self.client.post(url, self.data)
        url = reverse('reset_password')
        self.response = self.client.post(url, {'email': self.data['email']})

    def test_redirection(self):
        '''
        A valid form submission should redirect the user to `password_reset_done` view
        '''
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)


class InvalidPasswordResetTests(TestCase):
    def setUp(self):
        url = reverse('reset_password')
        self.response = self.client.post(url, {'email': 'donotexist@email.com'})

    def test_redirection(self):
        '''
        Even invalid emails in the database should
        redirect the user to `password_reset_done` view
        '''
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)

    def test_no_reset_email_sent(self):
        self.assertEqual(0, len(mail.outbox))


class PasswordResetConfirmTests(TestCase):
    def setUp(self):
        self.data = USER_DATA
        external_group = Group.objects.create(name="external users")
        user = User.objects.create_user(username=self.data['username'],
                                        email=self.data['email'],
                                        password=self.data['password1'],
                                        first_name=self.data['first_name'],
                                        last_name=self.data['last_name'])
        user.groups.add(external_group)
        self.uid = urlsafe_base64_encode(force_bytes(user.pk))
        self.token = default_token_generator.make_token(user)

        url = reverse('password_reset_confirm', kwargs={'uidb64': self.uid, 'token': self.token})
        self.response = self.client.get(url, follow=True)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/resetare-parola/{uidb64}/{token}/'.format(uidb64=self.uid, token=self.token))
        self.assertEquals(view.func.view_class, auth_views.PasswordResetConfirmView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SetPasswordForm)

    def test_form_inputs(self):
        '''
        The view must contain two inputs: csrf and two password fields
        '''
        self.assertContains(self.response, '<input', 5)
        self.assertContains(self.response, 'type="password"', 2)


class InvalidPasswordResetConfirmTests(TestCase):
    def setUp(self):
        self.data = USER_DATA
        external_group = Group.objects.create(name="studenti")
        user = User.objects.create_user(username=self.data['username'],
                                        email=self.data['email'],
                                        password=self.data['password1'],
                                        first_name=self.data['first_name'],
                                        last_name=self.data['last_name'])
        user.groups.add(external_group)

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        '''
        invalidate the token by changing the password
        '''
        user.set_password('abcdef123')
        user.save()
        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)


class PasswordResetCompleteTests(TestCase):
    def setUp(self):
        url = reverse('password_reset_complete')
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/resetare-parola-completa/')
        self.assertEquals(view.func.view_class, auth_views.PasswordResetCompleteView)
