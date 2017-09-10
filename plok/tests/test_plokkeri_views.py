from django.test import TestCase
from django.core.urlresolvers import reverse


class IndexPage(TestCase):
    def test_reverse_plokkeri(self):
        self.assertEqual(reverse('plok:index'), '/')

    def test_uses_correct_template(self):
        response = self.client.get(reverse('plok:index'))
        self.assertTemplateUsed(response, 'plok/index.html')
        # self.assertTemplateUsed(response, 'plok/article_list.html')
