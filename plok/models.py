from django.db import models
from django.contrib import auth
from django.utils.translation import ugettext_lazy
from django.conf import settings  # For available languages
from django.urls import reverse


class Blog(models.Model):
    name = models.SlugField(max_length=100, unique=True, verbose_name=ugettext_lazy('name'),
                            help_text=ugettext_lazy('Must be unique. Used in URL.'))
    title = models.CharField(max_length=250, verbose_name=ugettext_lazy('title'))
    description = models.TextField(null=True, blank=True, verbose_name=ugettext_lazy('description'))
    language = models.CharField(max_length=50, choices=settings.LANGUAGES, default='en',
                                verbose_name=ugettext_lazy('language'))
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE, related_name='blog_created_by')
    edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey(auth.get_user_model(), on_delete=models.SET_NULL, null=True,
                                  related_name='blog_edited_by')

    def articles(self):
        return Article.objects.filter(blog=self)

    def can_edit(self, user):
        if user == self.created_by:
            return True

        return False

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plok:blog', args=[self.name])

    def __str__(self):
        return self.name


class Article(models.Model):
    FORMAT_CHOICES = (
        ('html', 'HTML'),
        ('markdown', 'Markdown'),
    )

    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, null=False)
    name = models.SlugField(max_length=100, unique=True, verbose_name=ugettext_lazy('name'),
                            help_text=ugettext_lazy('Must be unique. Used in URL.'))
    title = models.CharField(max_length=250, verbose_name=ugettext_lazy('title'))
    description = models.TextField(null=True, blank=True,  # Short description, used in page meta headers
                                   verbose_name=ugettext_lazy('description'))
    text = models.TextField(null=True, blank=True, verbose_name=ugettext_lazy('text'))  # Actual blog content
    language = models.CharField(max_length=50, choices=settings.LANGUAGES, default='en',
                                verbose_name=ugettext_lazy('language'))
    format = models.CharField(max_length=50, choices=FORMAT_CHOICES, default='html')
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE, related_name='article_created_by')
    edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey(auth.get_user_model(), on_delete=models.SET_NULL, null=True,
                                  related_name='article_edited_by')

    @property
    def comments(self):
        comments = Comment.objects.filter(article=self).order_by('created')
        return comments

    def can_edit(self, user):
        if user == self.created_by:
            return True

        return False

    def __unicode__(self):
        return self.blog.name + ':' + self.name

    def get_absolute_url(self):
        return reverse('plok:article', args=[self.blog.name, self.name])

    def get_edit_url(self):
        return reverse('plok:article_update', args=[self.blog.name, self.name])

    def __str__(self):
        return '{}:{}'.format(self.blog.name, self.name)

    class Meta:
        ordering = ['-created']  # Default ordering by points (descending)


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=False)
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, default=None, blank=True)
    text = models.TextField(null=True, blank=True, verbose_name=ugettext_lazy('text'))  # Actual comment
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(auth.get_user_model(), on_delete=models.CASCADE, related_name='comment_created_by')
    edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey(auth.get_user_model(), on_delete=models.SET_NULL, null=True,
                                  related_name='comment_edited_by')

    def __str__(self):
        return '{}:{}'.format(self.article.name, self.created_by.username)
