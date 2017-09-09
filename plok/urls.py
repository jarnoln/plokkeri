from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .blog import BlogList, BlogDetail, BlogCreate, BlogUpdate, BlogDelete
from .article import ArticleList, ArticleDetail, ArticleCreate, ArticleUpdate, ArticleDelete
from .views import IndexView


urlpatterns = [
    url(r'^(?P<blog_name>\w+)/create_article/$', login_required(ArticleCreate.as_view()), name='article_create'),
    # url(r'^(?P<blog_name>\w+)/(?P<slug>\w+)/delete/$', login_required(ArticleDelete.as_view()), name='article_delete'),
    # url(r'^(?P<blog_name>\w+)/(?P<slug>\w+)/update/$', login_required(ArticleUpdate.as_view()), name='article_update'),
    url(r'^create/$', login_required(BlogCreate.as_view()), name='blog_create'),
    url(r'^list/$', BlogList.as_view(), name='blog_list'),
    url(r'^(?P<slug>\w+)/update/$', login_required(BlogUpdate.as_view()), name='blog_update'),
    url(r'^(?P<slug>\w+)/delete/$', login_required(BlogDelete.as_view()), name='blog_delete'),
    url(r'^(?P<blog_name>\w+)/(?P<slug>\w+)/$', ArticleDetail.as_view(), name='article'),
    url(r'^(?P<slug>.\w+)/$', BlogDetail.as_view(), name='blog'),
    url(r'^$', IndexView.as_view(), name='index'),
]
