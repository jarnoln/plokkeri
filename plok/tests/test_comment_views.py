# from unittest import skip
from django.test import TestCase
from django.conf import settings
from django.urls import reverse
from django.contrib import auth
from plok.models import Blog, Article, Comment
from .ext_test_case import ExtTestCase


class ArticlePageComments(ExtTestCase):
    url_name = 'plok:article'

    def test_article_page_includes_comments(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog")
        article = Article.objects.create(blog=blog, created_by=user, name="test_article", title="Test article",
                                         description="Article description", text="Some content")
        response = self.client.get(reverse(self.url_name, args=[blog.name, article.name]))
        self.assertContains(response, 'Comments: 0')
        comment = Comment.objects.create(article=article, created_by=user, text='Clever comment')
        response = self.client.get(reverse(self.url_name, args=[blog.name, article.name]))
        self.assertContains(response, article.title)
        self.assertContains(response, article.description)
        self.assertContains(response, article.text)
        self.assertContains(response, 'Comments: 1')
        self.assertContains(response, comment.text)


class CreateCommentPage(ExtTestCase):
    url_name = 'plok:comment_create'

    def test_reverse(self):
        self.assertEqual(reverse(self.url_name, args=['test_blog', 'test_article']),
                         '/plok/test_blog/test_article/comment/create/')

    def test_uses_correct_template(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog", title="Test blog")
        article = Article.objects.create(blog=blog, created_by=user, name="test_article", title="Test article",
                                         description="Article description", text="Some content")
        response = self.client.get(reverse(self.url_name, args=[blog.name, article.name]))
        self.assertTemplateUsed(response, 'plok/comment_form.html')

    def test_default_context(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog", title="Test blog")
        article = Article.objects.create(blog=blog, created_by=user, name="test_article", title="Test article",
                                         description="Article description", text="Some content")
        response = self.client.get(reverse(self.url_name, args=[blog.name, article.name]))
        self.assertEqual(response.context['message'], '')

    def test_can_create_new_comment(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog", title="Test blog")
        article = Article.objects.create(blog=blog, created_by=user, name="test_article", title="Test article",
                                         description="Article description", text="Some content")
        self.assertEqual(Comment.objects.all().count(), 0)
        response = self.client.post(reverse(
            self.url_name, args=[blog.name, article.name]),
            {
                'text': 'Clever comment'
            },
            follow=True)
        self.assertEqual(Comment.objects.all().count(), 1)
        self.assertEqual(Comment.objects.first().text, 'Clever comment')
        # self.assertEqual(response.context['article'].blog, blog)
        # self.assertEqual(response.context['article'].title, 'Test article')
        # self.assertEqual(response.context['article'].text, 'For testing')

    def test_cant_create_comment_if_not_logged_in(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog", description="Testing")
        article = Article.objects.create(blog=blog, created_by=creator, name="test_article", title="Test article",
                                         description="Article description", text="Some content")
        response = self.client.get(reverse(self.url_name, args=[blog.name, article.name]), follow=True)
        # self.assertTemplateUsed(response, 'registration/login.html')
        self.assertTemplateUsed(response, 'account/login.html')
