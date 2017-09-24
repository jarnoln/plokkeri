from django.test import TestCase
from django.core.urlresolvers import reverse


class IndexPage(TestCase):
    def test_reverse_plokkeri(self):
        self.assertEqual(reverse('plok:index'), '/')

    def test_uses_correct_template(self):
        response = self.client.get(reverse('plok:index'))
        # self.assertTemplateUsed(response, 'plok/index.html')
        self.assertTemplateUsed(response, 'plok/article_list.html')


class AboutPage(TestCase):
    url_name = 'plok:about'

    def test_reverse_plokkeri(self):
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
