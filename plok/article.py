import logging
from markdown import markdown
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, Http404
from django.utils.translation import ugettext
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from plok.models import Blog, Article


class ArticleList(ListView):
    model = Article
    context_object_name = 'article_list'

    def get_context_data(self, **kwargs):
        context = super(ArticleList, self).get_context_data(**kwargs)
        context['message'] = self.request.GET.get('message', '')
        context['page'] = "blogs"
        context['title'] = ugettext("Articles")
        context['can_add'] = self.request.user.is_superuser
        return context


class ArticleDetail(DetailView):
    model = Article
    slug_field = 'name'
    context_object_name = 'article'
    blog = None

    def get_queryset(self):
        self.blog = get_object_or_404(Blog, name=self.kwargs['blog_name'])
        return Article.objects.filter(blog=self.blog)

    def get_context_data(self, **kwargs):
        context = super(ArticleDetail, self).get_context_data(**kwargs)
        context['title'] = self.object.title
        context['description'] = self.object.description
        context['message'] = self.request.GET.get('message', '')
        context['can_edit'] = self.object.can_edit(self.request.user)
        if self.object.format == 'markdown':
            context['content'] = markdown(self.object.text)
        else:
            context['content'] = self.object.text
        return context


class ArticleCreate(CreateView):
    model = Article
    fields = ['name', 'title', 'text', 'description']
    blog = None

    def dispatch(self, request, *args, **kwargs):
        blog_name = kwargs['blog_name']
        self.blog = Blog.objects.get(name=blog_name)
        return super(ArticleCreate, self).dispatch(request,*args, **kwargs)

    def form_valid(self, form):
        form.instance.blog = self.blog
        form.instance.created_by = self.request.user
        if Article.objects.filter(blog=self.blog, name=form.instance.name).exists():
            logger = logging.getLogger(__name__)
            logger.warning("Article already exists: blog=%s name=%s" % (self.blog.name, form.instance.name))
            return super(ArticleCreate, self).form_invalid(form)
        else:
            return super(ArticleCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(ArticleCreate, self).get_context_data(**kwargs)
        context['message'] = self.request.GET.get('message', '')
        return context


class ArticleUpdate(UpdateView):
    model = Article
    slug_field = 'name'
    fields = ['title', 'text', 'description', 'format']
    blog = None

    def dispatch(self, request, *args, **kwargs):
        self.blog = get_object_or_404(Blog, name=self.kwargs['blog_name'])
        return super(ArticleUpdate, self).dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        if self.object.can_edit(self.request.user):
            return super(ArticleUpdate, self).render_to_response(context, **response_kwargs)
        else:
            return HttpResponseRedirect(reverse('plok:article', args=[self.blog.name, self.object.name]))

    def form_valid(self, form):
        logger = logging.getLogger(__name__)
        if self.object.can_edit(self.request.user):
            return super(ArticleUpdate, self).form_valid(form)
        else:
            logger.info("Not allowed to edit. Registered:%s Creator:%s" % (
                self.request.user.username, self.blog.created_by.username))
            return HttpResponseRedirect(reverse('plok:article', args=[self.blog.name, self.object.name]))


class ArticleDelete(DeleteView):
    slug_field = 'name'
    model = Article
    success_url = reverse_lazy('plok:index')

    def dispatch(self, request, *args, **kwargs):
        blog_name = kwargs['blog_name']
        self.blog = Blog.objects.get(name=blog_name)
        return super(ArticleDelete, self).dispatch(request,*args, **kwargs)

    def get_object(self):
        article = super(ArticleDelete, self).get_object()
        if article.can_edit(self.request.user):
            return article
        else:
            raise Http404

    def render_to_response(self, context, **response_kwargs):
        logger = logging.getLogger(__name__)
        if self.object.can_edit(self.request.user):
            context['blog'] = self.blog
            return super(ArticleDelete, self).render_to_response(context, **response_kwargs)
        else:
            logger.warning("User %s attempted to delete article created by %s" %
                           (self.request.user.username, self.blog.created_by.username))
            # return HttpResponseRedirect(reverse('plokkeri:blog', args=[self.blog.name]))
            return HttpResponseNotAllowed()
