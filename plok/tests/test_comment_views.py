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
        print(response.content)
        self.assertContains(response, article.title)
        self.assertContains(response, article.description)
        self.assertContains(response, article.text)
        self.assertContains(response, 'Comments: 1')
        self.assertContains(response, comment.text)
