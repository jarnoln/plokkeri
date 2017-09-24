# from unittest import skip
from django.test import TestCase
from django.core.urlresolvers import reverse
# from django.contrib.auth.models import User, AnonymousUser
from django.contrib import auth
from django.utils.translation import activate
from plok.models import Blog, Article
from .ext_test_case import ExtTestCase


class ArticleList(TestCase):
    url_name = 'plok:article_list'

    def test_reverse_blog_list(self):
        self.assertEqual(reverse(self.url_name), '/article_list/')

    def test_uses_correct_template(self):
        response = self.client.get(reverse(self.url_name))
        self.assertTemplateUsed(response, 'plok/article_list.html')

    def test_default_context(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog1 = Blog.objects.create(created_by=creator, name="test_blog_1", title="Test blog 1")
        blog2 = Blog.objects.create(created_by=creator, name="test_blog_2", title="Test blog 2")
        Article.objects.create(created_by=creator, blog=blog1, name="test_article_1", title="Test article 1")
        Article.objects.create(created_by=creator, blog=blog2, name="test_article_2", title="Test article 2")

        response = self.client.get(reverse(self.url_name))
        # self.assertEqual(response.context['page'], 'blogs')
        self.assertEqual(response.context['title'], 'Articles')
        self.assertEqual(response.context['article_list'].count(), 2)
        # self.assertEqual(response.context['article_list'][0], article2)  # Reverse ordering can't be tested
        # self.assertEqual(response.context['article_list'][1], article1)
        self.assertEqual(response.context['message'], '')
        # self.assertEqual(response.context['can_add'], True)
        self.assertEqual(response.context['can_add'], False)


class ArticlePage(ExtTestCase):
    url_name = 'plok:article'

    def test_reverse_article(self):
        self.assertEqual(reverse(self.url_name, args=['test_blog', 'test_article']),
                         '/plok/test_blog/test_article/')

    def test_get_absolute_url(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog")
        article = Article.objects.create(blog=blog, created_by=user, name="test_article")
        self.assertEqual(article.get_absolute_url(), reverse(self.url_name, args=['test_blog', 'test_article']))

    def test_uses_correct_template(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog")
        article = Article.objects.create(blog=blog, created_by=user, name="test_article")
        response = self.client.get(reverse(self.url_name, args=[blog.name, article.name]))
        self.assertTemplateUsed(response, 'plok/article_detail.html')

    def test_default_context(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog")
        article = Article.objects.create(blog=blog, created_by=user, name="test_article", title="Test article",
                                         description="Article description", text="Some content")
        response = self.client.get(reverse(self.url_name, args=['test_blog', 'test_article']))
        self.assertEqual(response.context['article'], article)
        self.assertEqual(response.context['article'].blog, blog)
        self.assertEqual(response.context['title'], 'Test article')
        self.assertEqual(response.context['description'], article.description)
        self.assertEqual(response.context['message'], '')
        self.assertContains(response, article.title)
        self.assertContains(response, article.description)
        self.assertContains(response, article.text)

    def test_404_no_blog_nor_article(self):
        response = self.client.get(reverse(self.url_name, args=['test_blog', 'test_article']))
        self.assertTemplateUsed(response, '404.html')


class CreateArticlePage(ExtTestCase):
    url_name = 'plok:article_create'

    def test_reverse_article_create(self):
        self.assertEqual(reverse(self.url_name, args=['test_blog']), '/plok/test_blog/create_article/')

    def test_uses_correct_template(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog", title="Test blog")
        response = self.client.get(reverse(self.url_name, args=[blog.name]))
        self.assertTemplateUsed(response, 'plok/article_form.html')

    def test_default_context(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog", title="Test blog")
        response = self.client.get(reverse(self.url_name, args=[blog.name]))
        self.assertEqual(response.context['message'], '')

    def test_can_create_new_article(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog", title="Test blog")
        self.assertEqual(Article.objects.all().count(), 0)
        response = self.client.post(reverse(
            self.url_name, args=[blog.name]),
            {
                'name': 'test_article',
                'blog_name': 'test_blog',
                'title': 'Test article',
                'text': 'For testing'
            },
            follow=True)
        self.assertEqual(Article.objects.all().count(), 1)
        self.assertEqual(response.context['article'].blog, blog)
        self.assertEqual(response.context['article'].title, 'Test article')
        self.assertEqual(response.context['article'].text, 'For testing')

    def test_cant_create_article_if_not_logged_in(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog", description="Testing")
        response = self.client.get(reverse(self.url_name, args=[blog.name]), follow=True)
        # self.assertTemplateUsed(response, 'registration/login.html')
        self.assertTemplateUsed(response, 'account/login.html')

    def test_cant_create_article_with_existing_name(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog", title="Test blog")
        Article.objects.create(created_by=user, blog=blog, name="test_article", title="Test article")
        self.assertEqual(Article.objects.all().count(), 1)
        response = self.client.post(
            reverse(self.url_name, args=[blog.name]),
            {
                'blog_name': blog.name,
                'name': 'test_article',
                'title': 'Test blog',
                'description': 'For testing'
            },
            follow=True)
        self.assertEqual(Article.objects.all().count(), 1)
        self.assertTemplateUsed(response, 'plok/article_form.html')
        #
        # self.assertContains(response, 'Article with this Name already exists')


class UpdateArticlePage(ExtTestCase):
    url_name = 'plok:article_update'

    def test_reverse_article_edit(self):
        self.assertEqual(reverse(self.url_name, args=['test_blog', 'test_article']),
                         '/plok/test_blog/test_article/update/')

    def test_get_edit_url(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog")
        article = Article.objects.create(blog=blog, created_by=user, name="test_article")
        self.assertEqual(article.get_edit_url(), reverse(self.url_name, args=['test_blog', 'test_article']))

    def test_uses_correct_template(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog")
        Article.objects.create(blog=blog, created_by=user, name="test_article")
        response = self.client.get(reverse(self.url_name, args=['test_blog', 'test_article']))
        self.assertTemplateUsed(response, 'plok/article_form.html')

    def test_default_context(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog")
        article = Article.objects.create(blog=blog, created_by=user, name="test_article")
        response = self.client.get(reverse(self.url_name, args=['test_blog', 'test_article']))
        self.assertEqual(response.context['article'], article)
        self.assertEqual(response.context['article'].blog, blog)
        # self.assertEqual(response.context['message'], '')

    def test_can_update_article(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog", title="Test blog", description="Testing")
        article = Article.objects.create(blog=blog, created_by=user, name="test_article", title="Test article")
        self.assertEqual(Blog.objects.all().count(), 1)
        response = self.client.post(reverse(self.url_name, args=[blog.name, article.name]),
                                    {'title': 'Article updated', 'text': 'Updated'},
                                    follow=True)
        self.assertEqual(Article.objects.all().count(), 1)
        article = Article.objects.all()[0]
        self.assertEqual(article.title, 'Article updated')
        self.assertEqual(article.text, 'Updated')
        self.assertTemplateUsed(response, 'plok/article_detail.html')
        self.assertEqual(response.context['article'].title, 'Article updated')
        self.assertEqual(response.context['article'].text, 'Updated')

    def test_cant_edit_without_logging_in(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog", description="Testing")
        article = Article.objects.create(created_by=creator, blog=blog, name="test_article", title="Test article")
        response = self.client.get(reverse(self.url_name, args=[blog.name, article.name]), follow=True)
        # self.assertTemplateUsed(response, 'registration/login.html')
        self.assertTemplateUsed(response, 'account/login.html')

    def test_cant_edit_article_if_not_creator(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog", description="Testing")
        article = Article.objects.create(created_by=creator, blog=blog, name="test_article", title="Test article")
        self.create_and_log_in_user()
        response = self.client.post(reverse(self.url_name, args=[blog.name, article.name]),
                                    {'title': 'New title', 'text': 'New text'},
                                    follow=True)
        self.assertTemplateUsed(response, 'plok/article_detail.html')
        article = Article.objects.all()[0]
        self.assertEqual(article.name, 'test_article')
        self.assertEqual(article.title, 'Test article')
        self.assertEqual(response.context['article'].title, 'Test article')
        self.assertEqual(response.context['article'].text, None)


class DeleteArticlePage(ExtTestCase):
    url_name = 'plok:article_delete'

    def test_reverse_blog_delete(self):
        self.assertEqual(reverse(self.url_name, args=['test_blog', 'test_article']),
                         '/plok/test_blog/test_article/delete/')

    def test_uses_correct_template(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog")
        article = Article.objects.create(created_by=user, blog=blog, name="test_article", title="Test article")
        response = self.client.get(reverse(self.url_name, args=[blog.name, article.name]))
        self.assertTemplateUsed(response, 'plok/article_confirm_delete.html')
        self.assertEqual(response.context['blog'], blog)
        self.assertEqual(response.context['article'], article)

    def test_404_no_article(self):
        user = self.create_and_log_in_user()
        Blog.objects.create(created_by=user, name="test_blog")
        response = self.client.get(reverse(self.url_name, args=['test_blog', 'test_article']))
        self.assertTemplateUsed(response, '404.html')

    def test_can_delete_article(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog", title="Test blog")
        article = Article.objects.create(created_by=user, blog=blog, name="test_article", title="Test article")
        self.assertEqual(Blog.objects.all().count(), 1)
        self.assertEqual(Article.objects.all().count(), 1)
        response = self.client.post(reverse(self.url_name, args=[blog.name, article.name]), {}, follow=True)
        self.assertTemplateUsed(response, 'plok/article_list.html')
        self.assertEqual(Blog.objects.all().count(), 1)
        self.assertEqual(Article.objects.all().count(), 0)

    def test_cant_delete_article_if_not_logged_in(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog", description="Testing")
        article = Article.objects.create(created_by=creator, blog=blog, name="test_article", title="Test article")
        response = self.client.post(reverse(self.url_name, args=[blog.name, article.name]), {}, follow=True)
        # self.assertTemplateUsed(response, 'registration/login.html')
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertEqual(Blog.objects.all().count(), 1)
        self.assertEqual(Article.objects.all().count(), 1)

    def test_cant_delete_article_if_not_creator(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog", description="Testing")
        article = Article.objects.create(created_by=creator, blog=blog, name="test_article", title="Test article")
        self.create_and_log_in_user()
        self.assertEqual(Blog.objects.all().count(), 1)
        self.assertEqual(Article.objects.all().count(), 1)
        response = self.client.post(reverse(self.url_name, args=[blog.name, article.name]), {}, follow=True)
        self.assertTemplateUsed(response, '404.html')
        self.assertEqual(Blog.objects.all().count(), 1)
        self.assertEqual(Article.objects.all().count(), 1)
