# from unittest import skip
from django.conf import settings
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.test import TestCase
from plok.models import Blog, Article
from .ext_test_case import ExtTestCase


class BlogList(TestCase):
    url_name = 'plok:blog_list'

    def test_reverse_blog_list(self):
        self.assertEqual(reverse(self.url_name), '/list/')

    def test_uses_correct_template(self):
        response = self.client.get(reverse(self.url_name))
        self.assertTemplateUsed(response, 'plok/blog_list.html')

    def test_default_context(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog1 = Blog.objects.create(created_by=creator, name="test_blog_1", title="Test blog 1")
        blog2 = Blog.objects.create(created_by=creator, name="test_blog_2", title="Test blog 2")
        response = self.client.get(reverse(self.url_name))
        self.assertEqual(response.context['page'], 'blogs')
        self.assertEqual(response.context['title'], 'Blogs')
        self.assertEqual(response.context['blog_list'].count(), 2)
        self.assertEqual(response.context['blog_list'][0], blog1)
        self.assertEqual(response.context['blog_list'][1], blog2)
        self.assertEqual(response.context['message'], '')
        # self.assertEqual(response.context['can_add'], True)
        self.assertEqual(response.context['can_add'], False)


class BlogPage(ExtTestCase):
    url_name = 'plok:blog'

    def test_reverse_blog(self):
        self.assertEqual(reverse(self.url_name, args=['test_blog']), '/plok/test_blog/')

    def test_uses_correct_template(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog")
        response = self.client.get(reverse(self.url_name, args=[blog.name]))
        self.assertTemplateUsed(response, 'plok/blog_detail.html')

    def test_get_absolute_url(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog")
        self.assertEqual(blog.get_absolute_url(), reverse(self.url_name, args=[blog.name]))

    def test_default_context(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog")
        response = self.client.get(reverse(self.url_name, args=[blog.name]))
        self.assertEqual(response.context['blog'], blog)
        self.assertEqual(response.context['blog'].articles().count(), 0)
        self.assertEqual(response.context['title'], 'Test blog')
        self.assertEqual(response.context['message'], '')
        self.assertEqual(response.context['can_edit'], False)

    def test_404_no_blog(self):
        response = self.client.get(reverse(self.url_name, args=['test_blog']))
        self.assertTemplateUsed(response, '404.html')

    def test_cant_edit_if_not_logged_in(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog")
        response = self.client.get(reverse(self.url_name, args=[blog.name]))
        self.assertEqual(response.context['can_edit'], False)

    def test_cant_edit_if_not_creator(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog")
        self.create_and_log_in_user()
        response = self.client.get(reverse(self.url_name, args=[blog.name]))
        self.assertEqual(response.context['can_edit'], False)

    def test_shows_articles(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog")
        article = Article.objects.create(blog=blog, name="test_article", title="Test article", created_by=creator)
        response = self.client.get(reverse(self.url_name, args=[blog.name]))
        self.assertEqual(response.context['blog'].articles().count(), 1)
        self.assertEqual(response.context['blog'].articles()[0], article)


class CreateBlogPage(ExtTestCase):
    url_name = 'plok:blog_create'

    def test_reverse_blog_create(self):
        self.assertEqual(reverse(self.url_name), '/create/')

    def test_uses_correct_template(self):
        self.create_and_log_in_user()
        response = self.client.get(reverse(self.url_name))
        self.assertTemplateUsed(response, 'plok/blog_form.html')

    def test_default_context(self):
        self.create_and_log_in_user()
        self.client.cookies.load({settings.LANGUAGE_COOKIE_NAME: 'en-us'})
        response = self.client.get(reverse(self.url_name))
        self.assertEqual(response.context['title'], 'Create new blog')
        self.assertEqual(response.context['message'], '')

    def test_can_create_new_blog(self):
        self.assertEqual(Blog.objects.all().count(), 0)
        self.create_and_log_in_user()
        response = self.client.post(reverse(self.url_name), {
            'name': 'test_blog',
            'title': 'Test blog',
            'description': 'For testing'},
                                    follow=True)
        self.assertEqual(Blog.objects.all().count(), 1)
        self.assertEqual(response.context['blog'].name, 'test_blog')
        self.assertEqual(response.context['blog'].title, 'Test blog')
        self.assertEqual(response.context['blog'].description, 'For testing')

    def test_cant_create_blog_if_not_logged_in(self):
        response = self.client.get(reverse(self.url_name), follow=True)
        self.assertTemplateUsed(response, 'account/login.html')

    def test_cant_create_blog_with_existing_name(self):
        user = self.create_and_log_in_user()
        Blog.objects.create(created_by=user, name="test_blog", title="Test blog")
        self.assertEqual(Blog.objects.all().count(), 1)
        self.client.cookies.load({settings.LANGUAGE_COOKIE_NAME: 'en-us'})
        response = self.client.post(
            reverse(self.url_name),
            {
                'name': 'test_blog',
                'title': 'Test blog',
                'description': 'For testing'
            },
            follow=True)
        self.assertEqual(Blog.objects.all().count(), 1)
        self.assertTemplateUsed(response, 'plok/blog_form.html')
        self.assertContains(response, 'Blog with this Name already exists')


class UpdateBlogPage(ExtTestCase):
    url_name = 'plok:blog_update'

    def test_reverse_blog_update(self):
        self.assertEqual(reverse(self.url_name, args=['test_blog']), '/plok/test_blog/update/')

    def test_uses_correct_template(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog")
        response = self.client.get(reverse(self.url_name, args=[blog.name]))
        self.assertTemplateUsed(response, 'plok/blog_form.html')

    def test_404_no_blog(self):
        self.create_and_log_in_user()
        response = self.client.get(reverse(self.url_name, args=['test_blog']))
        self.assertTemplateUsed(response, '404.html')

    def test_can_update_blog(self):
        user = self.create_and_log_in_user()
        Blog.objects.create(created_by=user, name="test_blog", title="Test blog", description="Testing")
        self.assertEqual(Blog.objects.all().count(), 1)
        response = self.client.post(reverse(self.url_name, args=['test_blog']), {
            'title': 'Test blog updated',
            'description': 'Updated'},
                                    follow=True)
        self.assertEqual(Blog.objects.all().count(), 1)
        blog = Blog.objects.all()[0]
        self.assertEqual(blog.title, 'Test blog updated')
        self.assertEqual(blog.description, 'Updated')
        self.assertTemplateUsed(response, 'plok/blog_detail.html')
        self.assertEqual(response.context['blog'].title, 'Test blog updated')
        self.assertEqual(response.context['blog'].description, 'Updated')

    def test_cant_update_blog_if_not_logged_in(self):
        creator = auth.get_user_model().objects.create(username='creator')
        Blog.objects.create(created_by=creator, name="test_blog", title="Test blog", description="Testing")
        response = self.client.post(reverse(self.url_name, args=['test_blog']), {
                                    'title': 'Test blog updated',
                                    'description': 'Updated'},
                                    follow=True)
        blog = Blog.objects.all()[0]
        self.assertEqual(blog.title, 'Test blog')
        self.assertEqual(blog.description, 'Testing')
        self.assertTemplateUsed(response, 'account/login.html')
        # self.assertTemplateUsed(response, 'registration/login.html')

    def test_cant_update_blog_if_not_creator(self):
        creator = auth.get_user_model().objects.create(username='creator')
        Blog.objects.create(created_by=creator, name="test_blog", title="Test blog", description="Testing")
        self.create_and_log_in_user()
        response = self.client.post(reverse(self.url_name, args=['test_blog']), {
                                    'title': 'Test blog updated',
                                    'description': 'Updated'},
                                    follow=True)
        self.assertTemplateUsed(response, 'plok/blog_detail.html')


class DeleteBlogPage(ExtTestCase):
    url_name = 'plok:blog_delete'

    def test_reverse_blog_delete(self):
        self.assertEqual(reverse(self.url_name, args=['test_blog']), '/plok/test_blog/delete/')

    def test_uses_correct_template(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog")
        response = self.client.get(reverse(self.url_name, args=[blog.name]))
        self.assertTemplateUsed(response, 'plok/blog_confirm_delete.html')

    def test_404_no_blog(self):
        user = self.create_and_log_in_user()
        response = self.client.get(reverse(self.url_name, args=['test_blog']))
        self.assertTemplateUsed(response, '404.html')

    def test_can_delete_blog(self):
        user = self.create_and_log_in_user()
        Blog.objects.create(created_by=user, name="test_blog", title="Test blog", description="Testing")
        self.assertEqual(Blog.objects.all().count(), 1)
        response = self.client.post(reverse(self.url_name, args=['test_blog']), {}, follow=True)
        self.assertEqual(Blog.objects.all().count(), 0)

    def test_cant_delete_blog_if_not_logged_in(self):
        creator = auth.get_user_model().objects.create(username='creator')
        Blog.objects.create(created_by=creator, name="test_blog", title="Test blog", description="Testing")
        response = self.client.post(reverse(self.url_name, args=['test_blog']), {}, follow=True)
        # self.assertTemplateUsed(response, 'registration/login.html')
        self.assertTemplateUsed(response, 'account/login.html')

    def test_cant_delete_blog_if_not_creator(self):
        creator = auth.get_user_model().objects.create(username='creator')
        Blog.objects.create(created_by=creator, name="test_blog", title="Test blog", description="Testing")
        user = self.create_and_log_in_user()
        self.assertEqual(Blog.objects.all().count(), 1)
        response = self.client.post(reverse(self.url_name, args=['test_blog']), {}, follow=True)
        self.assertEqual(Blog.objects.all().count(), 1)
        self.assertTemplateUsed(response, '404.html')

    def test_cant_delete_blog_if_blog_has_articles(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog", title="Test blog", description="Testing")
        article = Article.objects.create(created_by=user, blog=blog, name="test_article", title="Test article")
        self.assertEqual(Blog.objects.all().count(), 1)
        self.assertEqual(Article.objects.all().count(), 1)
        response = self.client.post(reverse(self.url_name, args=['test_blog']), {}, follow=True)
        self.assertEqual(Blog.objects.all().count(), 1)
        self.assertEqual(Article.objects.all().count(), 1)
        self.assertTemplateUsed(response, '404.html')
