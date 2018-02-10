from django.test import TestCase
from django.urls import reverse
from django.contrib import auth


class ExtTestCase(TestCase):
    def create_and_log_in_user(self):
        user = auth.models.User.objects.create(username='test_user', email='tuser@iki.fi')
        user.set_password('password')
        user.save()
        self.client.post(reverse('account_login'), {'login': user.username, 'password': 'password'})
        # html = response.content.decode('utf8')
        # print(html)
        return user
