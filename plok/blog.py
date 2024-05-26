import logging

from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import gettext
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from plok.models import Blog


class BlogList(ListView):
    model = Blog
    context_object_name = 'blog_list'

    def get_context_data(self, **kwargs):
        context = super(BlogList, self).get_context_data(**kwargs)
        context['message'] = self.request.GET.get('message', '')
        context['page'] = "blogs"
        context['title'] = "Blogs"
        context['can_add'] = self.request.user.is_superuser
        return context


class BlogDetail(DetailView):
    model = Blog
    slug_field = 'name'
    fields = ['name', 'title', 'description']
    context_object_name = 'blog'

    def get_context_data(self, **kwargs):
        context = super(BlogDetail, self).get_context_data(**kwargs)
        context['title'] = self.object.title
        context['message'] = self.request.GET.get('message', '')
        context['can_edit'] = self.object.can_edit(self.request.user)
        context['articles'] = self.object.articles()
        return context


class BlogCreate(CreateView):
    model = Blog
    slug_field = 'name'
    fields = ['name', 'title', 'description']

    def get_context_data(self, **kwargs):
        context = super(BlogCreate, self).get_context_data(**kwargs)
        context['title'] = gettext('Create new blog')
        context['message'] = self.request.GET.get('message', '')
        return context

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(BlogCreate, self).form_valid(form)


class BlogUpdate(UpdateView):
    model = Blog
    slug_field = 'name'
    fields = ['title', 'description']

    def render_to_response(self, context, **response_kwargs):
        # logger = logging.getLogger(__name__)
        # logger.warning('Tadaa!')
        if self.object.can_edit(self.request.user):
            return super(BlogUpdate, self).render_to_response(context, **response_kwargs)
        else:
            return HttpResponseRedirect(reverse('plok:blog', args=[self.object.name]))

    def form_valid(self, form):
        if self.object.can_edit(self.request.user):
            return super(BlogUpdate, self).form_valid(form)
        else:
            return HttpResponseRedirect(reverse('plok:blog', args=[self.object.name]))


class BlogDelete(DeleteView):
    slug_field = 'name'
    model = Blog
    success_url = reverse_lazy('plok:index')

    def render_to_response(self, context, **response_kwargs):
        if self.object.can_edit(self.request.user):
            if self.object.articles().count() == 0:
                return super(BlogDelete, self).render_to_response(context, **response_kwargs)

        return HttpResponseRedirect(reverse('plok:blog', args=[object.name]))

    def get_object(self):
        blog = super(BlogDelete, self).get_object()
        if blog.can_edit(self.request.user):
            if blog.articles().count() == 0:
                return blog

        # Todo: Smarter way to handle this
        raise Http404
