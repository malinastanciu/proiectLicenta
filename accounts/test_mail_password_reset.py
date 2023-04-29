from django.contrib.auth.models import Group, User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.urls import reverse
from django.urls import resolve
from django.test import TestCase
from django.contrib.auth import views as auth_views
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


class PasswordResetMailTests(TestCase):
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
        external_group = Group.objects.create(name="external users")
        user = User.objects.create_user(username=self.data['username'],
                                        email=self.data['email'],
                                        password=self.data['password1'],
                                        first_name=self.data['first_name'],
                                        last_name=self.data['last_name'])
        user.groups.add(external_group)

        self.uid = urlsafe_base64_encode(force_bytes(user.pk))
        self.token = default_token_generator.make_token(user)
        mail.send_mail('[Django Boards] Please reset your password',
                       reverse('password_reset_confirm', kwargs={'uidb64': self.uid, 'token': self.token}),
                       'from@example.com', ['john@doe.com'],
                       fail_silently=False)
        self.email = mail.outbox[0]

    def test_email_subject(self):
        self.assertEqual('[Django Boards] Please reset your password', self.email.subject)

    def test_email_body(self):
        token = self.token
        uid = self.uid
        password_reset_token_url = reverse('password_reset_confirm', kwargs={
            'uidb64': uid,
            'token': token
        })
        self.assertIn(password_reset_token_url, self.email.body)
        self.assertIn('john@doe.com', self.email.to)

    def test_email_to(self):
        self.assertEqual(['john@doe.com', ], self.email.to)


class PasswordResetDoneTests(TestCase):
    def setUp(self):
        url = reverse('password_reset_done')
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/resetare-parola-trimisa/')
        self.assertEquals(view.func.view_class, auth_views.PasswordResetDoneView)
