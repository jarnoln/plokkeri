#from unittest import skip
from django.db import IntegrityError
from django.contrib import auth
from plok.models import Blog, Article
from .ext_test_case import ExtTestCase


class BlogTests(ExtTestCase):
    def can_save_and_load_blog(self):
        creator = auth.get_user_model().objects.create(username='creator')
        self.assertEqual(Blog.objects.all().count(), 0)
        blog = Blog(created_by=creator, name="test_blog")
        blog.save()
        self.assertEqual(Blog.objects.all().count(), 1)

    def test_string(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog")
        self.assertEqual(str(blog), blog.name)

    def test_saving_blog_without_name_or_creator_fails(self):
        blog = Blog()
        with self.assertRaises(IntegrityError):
            blog.save()

    def test_saving_blog_with_existing_name_fails(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog1 = Blog(created_by=creator, name="test_blog")
        blog1.save()
        self.assertEqual(Blog.objects.all().count(), 1)
        blog2 = Blog(created_by=creator, name="test_blog")
        with self.assertRaises(IntegrityError):
            blog2.save()

    def test_blog_articles(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog")
        self.assertEqual(blog.articles().count(), 0)
        article = Article.objects.create(blog=blog, name="test_article", title="Test article", created_by=creator)
        self.assertEqual(blog.articles().count(), 1)
        self.assertEqual(blog.articles()[0], article)


class ArticleTests(ExtTestCase):
    def can_save_and_load_article(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog")
        self.assertEqual(Article.objects.all().count(), 0)
        article = Article(blog=blog, created_by=creator, slug="test_article")
        article.save()
        self.assertEqual(Article.objects.all().count(), 1)

    def test_string(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog")
        article = Article.objects.create(blog=blog, created_by=creator, name="test_article")
        self.assertEqual(str(article), '{}:{}'.format(blog.name, article.name))

    def test_saving_article_without_name_or_creator_fails(self):
        article = Article()
        with self.assertRaises(IntegrityError):
            article.save()
