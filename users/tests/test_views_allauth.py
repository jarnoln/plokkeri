from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib import auth
from .ext_test_case import ExtTestCase

# Django allauth views:
# http://django-allauth.readthedocs.io/en/latest/views.html


class SignupTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('account_signup'), '/accounts/signup/')

    def test_default_content(self):
        self.client.cookies.load({settings.LANGUAGE_COOKIE_NAME: 'en-us'})
        response = self.client.get(reverse('account_signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign Up')
        html = response.content.decode('utf8')
        # print(html)
        self.assertTrue(html.startswith('<!DOCTYPE html>'))

    def test_uses_correct_template(self):
        response = self.client.get(reverse('account_signup'))
        self.assertTemplateUsed(response, 'account/signup.html')

    def test_signup(self):
        self.assertEqual(auth.models.User.objects.count(), 0)
        response = self.client.post(reverse('account_signup'), {
            'username': 'user',
            'email': 'user@iki.fi',
            'password1': 'password',
            'password2': 'password'}, follow=True)
        self.assertEqual(auth.models.User.objects.count(), 1)
        self.assertTrue(response.context['user'].is_authenticated())
        self.assertEqual(response.context['user'], auth.models.User.objects.first())
        html = response.content.decode('utf8')
        self.assertInHTML('Logout', html)


class LoginTest(TestCase):
    def test_reverse(self):
        self.assertEqual(reverse('account_login'), '/accounts/login/')

    def test_default_content(self):
        self.client.cookies.load({settings.LANGUAGE_COOKIE_NAME: 'en-us'})
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign In')
        html = response.content.decode('utf8')
        # print(html)
        self.assertTrue(html.startswith('<!DOCTYPE html>'))

    def test_uses_correct_template(self):
        response = self.client.get(reverse('account_login'))
        self.assertTemplateUsed(response, 'account/login.html')

    def test_login(self):
        user = auth.models.User.objects.create(username='user', email='user@iki.fi')
        user.set_password('password')
        user.save()
        response = self.client.post(reverse('account_login'), {
            'login': user.username,
            'password': 'password',
            'next': reverse('plok:index')}, follow=True)
        self.assertTrue(response.context['user'].is_authenticated())
        self.assertEqual(response.context['user'], user)
        html = response.content.decode('utf8')
        self.assertInHTML('Logout', html)


class EmailManagementTest(ExtTestCase):
    def test_reverse(self):
        self.assertEqual(reverse('account_email'), '/accounts/email/')

    def test_uses_correct_template(self):
        self.create_and_log_in_user()
        response = self.client.get(reverse('account_email'), follow=True)
        self.assertTemplateUsed(response, 'account/email.html')

    def test_redirect_to_login_if_not_logged_in(self):
        response = self.client.get(reverse('account_email'), follow=True)
        self.assertTemplateUsed(response, 'account/login.html')


class SocialConnectionsTest(ExtTestCase):
    def test_reverse(self):
        self.assertEqual(reverse('socialaccount_connections'), '/accounts/social/connections/')

    def test_uses_correct_template(self):
        self.create_and_log_in_user()
        response = self.client.get(reverse('socialaccount_connections'), follow=True)
        self.assertTemplateUsed(response, 'socialaccount/connections.html')

    def test_redirect_to_login_if_not_logged_in(self):
        response = self.client.get(reverse('socialaccount_connections'), follow=True)
        self.assertTemplateUsed(response, 'account/login.html')
