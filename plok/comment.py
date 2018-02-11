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


class CommentUpdate(UpdateView):
    model = Comment
    fields = ['text']
    article = None

    def dispatch(self, request, *args, **kwargs):
        blog_name = kwargs['blog_name']
        article_name = kwargs['article_name']
        blog = Blog.objects.get(name=blog_name)
        self.article = Article.objects.get(blog=blog, name=article_name)
        return super(CommentUpdate, self).dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        if self.object.can_edit(self.request.user):
            return super(CommentUpdate, self).render_to_response(context, **response_kwargs)
        else:
            return HttpResponseRedirect(reverse('plok:article', args=[self.article.blog.name, self.article.name]))

    def form_valid(self, form):
        logger = logging.getLogger(__name__)
        form.instance.edited_by = self.request.user
        if self.object.can_edit(self.request.user):
            return super(CommentUpdate, self).form_valid(form)
        else:
            logger.info("Not allowed to edit. Registered:%s Creator:%s" % (
                self.request.user.username, self.blog.created_by.username))
            return HttpResponseRedirect(reverse('plok:article', args=[self.article.blog.name, self.article.name]))

    def get_context_data(self, **kwargs):
        context = super(CommentUpdate, self).get_context_data(**kwargs)
        context['message'] = self.request.GET.get('message', '')
        return context

    def get_success_url(self):
        return self.article.get_absolute_url()


class CommentDelete(DeleteView):
    # slug_field = 'name'
    model = Comment
    article = None

    def dispatch(self, request, *args, **kwargs):
        blog_name = kwargs['blog_name']
        article_name = kwargs['article_name']
        blog = Blog.objects.get(name=blog_name)
        self.article = Article.objects.get(blog=blog, name=article_name)
        return super(CommentDelete, self).dispatch(request,*args, **kwargs)

    def get_object(self):
        comment = super(CommentDelete, self).get_object()
        if comment.can_edit(self.request.user):
            return comment
        else:
            raise Http404

    def render_to_response(self, context, **response_kwargs):
        logger = logging.getLogger(__name__)
        if self.object.can_edit(self.request.user):
            # context['blog'] = self.blog
            return super(CommentDelete, self).render_to_response(context, **response_kwargs)
        else:
            logger.warning("User %s attempted to delete comment created by %s" %
                           (self.request.user.username, self.object.created_by.username))
            # return HttpResponseRedirect(reverse('plokkeri:blog', args=[self.blog.name]))
            return HttpResponseNotAllowed()

    def get_success_url(self):
        return self.article.get_absolute_url()
