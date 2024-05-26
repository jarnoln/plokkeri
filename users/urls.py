from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import UserList, UserDetail, UserUpdate, UserDelete


urlpatterns = [
    path("user/<slug:slug>/edit/", login_required(UserUpdate.as_view()), name='user_update'),
    path("user/<slug:slug>/delete/", login_required(UserDelete.as_view()), name='user_delete'),
    path("user/<slug:slug>/", UserDetail.as_view(), name='user_detail'),
    path("users/", login_required(UserList.as_view()), name='user_list'),
    path("accounts/profile/", login_required(UserDetail.as_view()), name='profile'),
]
