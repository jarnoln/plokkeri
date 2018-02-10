from django.test import TestCase
from django.urls import reverse
from django.utils import translation


class IndexPage(TestCase):
    def test_reverse_plokkeri(self):
        self.assertEqual(reverse('plok:index'), '/')

    def test_uses_correct_template(self):
        response = self.client.get(reverse('plok:index'))
        # self.assertTemplateUsed(response, 'plok/index.html')
        self.assertTemplateUsed(response, 'plok/article_list.html')


class AboutPage(TestCase):
    url_name = 'plok:about'

    def test_reverse(self):
        self.assertEqual(reverse(self.url_name), '/about/')

    def test_default_content(self):
        response = self.client.get(reverse(self.url_name))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Plokkeri')
        html = response.content.decode('utf8')
        # print(html)
        self.assertTrue(html.startswith('<!DOCTYPE html>'))

    def test_uses_correct_template(self):
        response = self.client.get(reverse(self.url_name))
        self.assertTemplateUsed(response, 'plok/about.html')


class ChangeLanguage(TestCase):
    url_name = 'set_language'

    def test_reverse(self):
        self.assertEqual(reverse(self.url_name), '/i18n/setlang/')

    def test_change_language(self):
        response = self.client.get(reverse('plok:index'))
        self.assertEqual(translation.get_language(), 'fi')
        self.assertEqual(response.context['title'], 'Jutut')
        response = self.client.post(reverse(self.url_name), data={
            'language': 'en',
            'next': reverse('plok:index')
        }, follow=True)
        self.assertTemplateUsed(response, 'plok/article_list.html')
        self.assertEqual(response.context['title'], 'Articles')
        response = self.client.post(reverse(self.url_name), data={
            'language': 'fi',
            'next': reverse('plok:index')
        }, follow=True)
        self.assertEqual(response.context['title'], 'Jutut')
