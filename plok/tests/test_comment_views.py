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
        self.assertContains(response, 'Clever comment')
        self.assertEqual(response.context['article'], article)

    def test_cant_create_comment_if_not_logged_in(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog", description="Testing")
        article = Article.objects.create(blog=blog, created_by=creator, name="test_article", title="Test article",
                                         description="Article description", text="Some content")
        response = self.client.get(reverse(self.url_name, args=[blog.name, article.name]), follow=True)
        # self.assertTemplateUsed(response, 'registration/login.html')
        self.assertTemplateUsed(response, 'account/login.html')


class UpdateCommentPage(ExtTestCase):
    url_name = 'plok:comment_update'

    def test_reverse(self):
        self.assertEqual(reverse(self.url_name, args=['test_blog', 'test_article', '1']),
                         '/plok/test_blog/test_article/comment/1/edit/')

    def test_edit_url(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog")
        article = Article.objects.create(blog=blog, created_by=user, name="test_article")
        comment = Comment.objects.create(article=article, created_by=user, text='Old comment')
        self.assertEqual(comment.edit_url, reverse(self.url_name, args=[blog.name, article.name, comment.id]))

    def test_uses_correct_template(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog", title="Test blog")
        article = Article.objects.create(blog=blog, created_by=user, name="test_article", title="Test article",
                                         description="Article description", text="Some content")
        comment = Comment.objects.create(article=article, created_by=user, text='Old comment')
        response = self.client.get(reverse(self.url_name, args=[blog.name, article.name, comment.id]))
        self.assertTemplateUsed(response, 'plok/comment_form.html')

    def test_default_context(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog", title="Test blog")
        article = Article.objects.create(blog=blog, created_by=user, name="test_article", title="Test article",
                                         description="Article description", text="Some content")
        comment = Comment.objects.create(article=article, created_by=user, text='Old comment')
        response = self.client.get(reverse(self.url_name, args=[blog.name, article.name, comment.id]))
        self.assertEqual(response.context['message'], '')

    def test_can_update_comment(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog", title="Test blog")
        article = Article.objects.create(blog=blog, created_by=user, name="test_article", title="Test article",
                                         description="Article description", text="Some content")
        comment = Comment.objects.create(article=article, created_by=user, text='Old comment')
        response = self.client.post(reverse(
            self.url_name, args=[blog.name, article.name, comment.id]),
            {
                'text': 'New comment'
            },
            follow=True)
        self.assertEqual(Comment.objects.all().count(), 1)
        self.assertEqual(Comment.objects.first().text, 'New comment')
        # self.assertEqual(response.context['article'].blog, blog)
        # self.assertEqual(response.context['article'].title, 'Test article')
        # self.assertEqual(response.context['article'].text, 'For testing')

    def test_cant_create_comment_if_not_logged_in(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog", description="Testing")
        article = Article.objects.create(blog=blog, created_by=creator, name="test_article", title="Test article",
                                         description="Article description", text="Some content")
        comment = Comment.objects.create(article=article, created_by=creator, text='Old comment')
        response = self.client.get(reverse(self.url_name, args=[blog.name, article.name, comment.id]), follow=True)
        # self.assertTemplateUsed(response, 'registration/login.html')
        self.assertTemplateUsed(response, 'account/login.html')


class DeleteCommentPage(ExtTestCase):
    url_name = 'plok:comment_delete'

    def test_reverse_blog_delete(self):
        self.assertEqual(reverse(self.url_name, args=['test_blog', 'test_article', '1']),
                         '/plok/test_blog/test_article/comment/1/delete/')

    def test_uses_correct_template(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog")
        article = Article.objects.create(created_by=user, blog=blog, name="test_article", title="Test article")
        comment = Comment.objects.create(article=article, created_by=user, text='Clever comment')
        response = self.client.get(reverse(self.url_name, args=[blog.name, article.name, comment.id]))
        self.assertTemplateUsed(response, 'plok/comment_confirm_delete.html')
        # self.assertEqual(response.context['blog'], blog)
        # self.assertEqual(response.context['article'], article)

    def test_404(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog")
        article = Article.objects.create(created_by=user, blog=blog, name="test_article", title="Test article")
        response = self.client.get(reverse(self.url_name, args=[blog.name, article.name, '1']))
        self.assertTemplateUsed(response, '404.html')

    def test_can_delete_comment(self):
        user = self.create_and_log_in_user()
        blog = Blog.objects.create(created_by=user, name="test_blog", title="Test blog")
        article = Article.objects.create(created_by=user, blog=blog, name="test_article", title="Test article")
        comment = Comment.objects.create(article=article, created_by=user, text='Clever comment')
        self.assertEqual(Blog.objects.all().count(), 1)
        self.assertEqual(Article.objects.all().count(), 1)
        self.assertEqual(Comment.objects.all().count(), 1)
        response = self.client.post(reverse(self.url_name, args=[blog.name, article.name, comment.id]), {}, follow=True)
        self.assertTemplateUsed(response, 'plok/article_detail.html')
        self.assertEqual(response.context['article'], article)
        self.assertEqual(Blog.objects.all().count(), 1)
        self.assertEqual(Article.objects.all().count(), 1)
        self.assertEqual(Comment.objects.all().count(), 0)

    def test_cant_delete_article_if_not_logged_in(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog", description="Testing")
        article = Article.objects.create(created_by=creator, blog=blog, name="test_article", title="Test article")
        comment = Comment.objects.create(article=article, created_by=creator, text='Clever comment')
        response = self.client.post(reverse(self.url_name, args=[blog.name, article.name, comment.id]), {}, follow=True)
        # self.assertTemplateUsed(response, 'registration/login.html')
        self.assertTemplateUsed(response, 'account/login.html')
        self.assertEqual(Blog.objects.all().count(), 1)
        self.assertEqual(Article.objects.all().count(), 1)
        self.assertEqual(Comment.objects.all().count(), 1)

    def test_cant_delete_article_if_not_creator(self):
        creator = auth.get_user_model().objects.create(username='creator')
        blog = Blog.objects.create(created_by=creator, name="test_blog", title="Test blog", description="Testing")
        article = Article.objects.create(created_by=creator, blog=blog, name="test_article", title="Test article")
        comment = Comment.objects.create(article=article, created_by=creator, text='Clever comment')
        self.create_and_log_in_user()
        self.assertEqual(Blog.objects.all().count(), 1)
        self.assertEqual(Article.objects.all().count(), 1)
        self.assertEqual(Comment.objects.all().count(), 1)
        response = self.client.post(reverse(self.url_name, args=[blog.name, article.name, comment.id]), {}, follow=True)
        self.assertTemplateUsed(response, '404.html')
        self.assertEqual(Blog.objects.all().count(), 1)
        self.assertEqual(Article.objects.all().count(), 1)
        self.assertEqual(Comment.objects.all().count(), 1)
