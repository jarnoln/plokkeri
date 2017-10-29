from django.core.urlresolvers import reverse, reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import UpdateView, DeleteView
from django.http import Http404
from django.contrib import auth
from django.shortcuts import get_object_or_404


def can_edit_user(logged_user, target_user):
    """ Is logged in user allowed to edit target user """
    if logged_user == target_user:
        return True
    if logged_user.is_staff:
        return True
    return False


class UserList(ListView):
    model = auth.get_user_model()

    def get_context_data(self, **kwargs):
        context = super(UserList, self).get_context_data(**kwargs)
        context['messages'] = self.request.GET.get('message', '')
        return context


class UserDetail(DetailView):
    template_name = 'auth/profile.html'
    context_object_name = 'target_user'

    def get_object(self, queryset=None):
        target_username = self.kwargs.get('slug', '')
        if target_username:
            # return auth.models.User.objects.get(username=target_username)
            target_user = get_object_or_404(auth.get_user_model(), username=target_username)
            return target_user

        return auth.get_user(self.request)


class UserUpdate(UpdateView):
    model = auth.get_user_model()
    slug_field = 'username'
    fields = ['first_name', 'last_name']

    def get_object(self):
        target_user = super(UserUpdate, self).get_object()
        if can_edit_user(logged_user=self.request.user, target_user=target_user):
            return target_user

        # Todo: Smarter way to handle this
        raise Http404

    def get_context_data(self, **kwargs):
        context = super(UserUpdate, self).get_context_data(**kwargs)
        context['message'] = self.request.GET.get('message', '')
        return context

    def get_success_url(self):
        if self.object:
            return reverse_lazy('user_detail', args=[self.object.username])
        else:
            return reverse('user_list')


class UserDelete(DeleteView):
    slug_field = 'username'
    model = auth.models.User
    success_url = reverse_lazy('plok:index')

    def get_object(self):
        target_user = super(UserDelete, self).get_object()
        if can_edit_user(logged_user=self.request.user, target_user=target_user):
            return target_user

        # Todo: Smarter way to handle this
        raise Http404

    def render_to_response(self, context, **response_kwargs):
        return super(UserDelete, self).render_to_response(context, **response_kwargs)
