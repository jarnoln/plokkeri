from django.db import models
# from django.contrib.auth.models import User
from django.contrib import auth
from django.utils.translation import ugettext_lazy
from django.conf import settings  # For available languages
from django.core.urlresolvers import reverse


class Blog(models.Model):
    name = models.SlugField(max_length=100, unique=True, verbose_name=ugettext_lazy('name'),
                            help_text=ugettext_lazy('Must be unique. Used in URL.'))
    title = models.CharField(max_length=250, verbose_name=ugettext_lazy('title'))
    description = models.TextField(null=True, blank=True, verbose_name=ugettext_lazy('description'))
    language = models.CharField(max_length=50, choices=settings.LANGUAGES, default='en',
                                verbose_name=ugettext_lazy('language'))
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(auth.get_user_model(), related_name='blog_created_by')
    edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey(auth.get_user_model(), null=True, related_name='blog_edited_by')

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

    blog = models.ForeignKey(Blog, null=False)
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
    created_by = models.ForeignKey(auth.get_user_model(), related_name='article_created_by')
    edited = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey(auth.get_user_model(), null=True, related_name='article_edited_by')

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
