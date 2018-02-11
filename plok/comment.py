import logging
from markdown import markdown
from django.urls import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponseNotAllowed, Http404
from django.utils.translation import ugettext
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from plok.models import Blog, Article, Comment


class CommentCreate(CreateView):
    model = Comment
    fields = ['text']
    article = None

    def dispatch(self, request, *args, **kwargs):
        blog_name = kwargs['blog_name']
        article_name = kwargs['article_name']
        blog = Blog.objects.get(name=blog_name)
        self.article = Article.objects.get(blog=blog, name=article_name)
        return super(CommentCreate, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.article = self.article
        form.instance.created_by = self.request.user
        return super(CommentCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(CommentCreate, self).get_context_data(**kwargs)
        context['message'] = self.request.GET.get('message', '')
        return context

    def get_success_url(self):
        return self.article.get_absolute_url()
