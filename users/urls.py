from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views import UserList, UserDetail, UserUpdate, UserDelete


urlpatterns = [
    url(r'^user/(?P<slug>[\w]+)/edit/$', login_required(UserUpdate.as_view()), name='user_update'),
    url(r'^user/(?P<slug>[\w]+)/delete/$', login_required(UserDelete.as_view()), name='user_delete'),
    url(r'^user/(?P<slug>[\w]+)/$', UserDetail.as_view(), name='user_detail'),
    url(r'^users/$', login_required(UserList.as_view()), name='user_list'),
    url(r'^accounts/profile/$', login_required(UserDetail.as_view()), name='profile'),
]
