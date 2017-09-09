from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views import IndexView


urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
]
