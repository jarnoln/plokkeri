from django.urls import path
from django.contrib.auth.decorators import login_required
from .blog import BlogList, BlogDetail, BlogCreate, BlogUpdate, BlogDelete
from .article import ArticleList, ArticleDetail, ArticleCreate, ArticleUpdate, ArticleDelete
from .comment import CommentCreate, CommentUpdate
from .about import AboutView


app_name = 'plok'
urlpatterns = [
    path('create/', login_required(BlogCreate.as_view()), name='blog_create'),
    path('list/', BlogList.as_view(), name='blog_list'),
    path('article_list/', ArticleList.as_view(), name='article_list'),
    path('about/', AboutView.as_view(), name='about'),
    path('plok/<slug:slug>/update/', login_required(BlogUpdate.as_view()), name='blog_update'),
    path('plok/<slug:slug>/delete/', login_required(BlogDelete.as_view()), name='blog_delete'),
    path('plok/<slug:blog_name>/create_article/', login_required(ArticleCreate.as_view()), name='article_create'),
    path('plok/<slug:slug>/', BlogDetail.as_view(), name='blog'),
    path('plok/<slug:blog_name>/<slug:slug>/delete/',
         login_required(ArticleDelete.as_view()), name='article_delete'),
    path('plok/<slug:blog_name>/<slug:slug>/update/',
         login_required(ArticleUpdate.as_view()), name='article_update'),
    path('plok/<slug:blog_name>/<slug:article_name>/comment/<int:pk>/edit/',
         login_required(CommentUpdate.as_view()), name='comment_update'),
    path('plok/<slug:blog_name>/<slug:article_name>/comment/create/',
         login_required(CommentCreate.as_view()), name='comment_create'),
    path('plok/<slug:blog_name>/<slug:slug>/', ArticleDetail.as_view(), name='article'),
    path('', ArticleList.as_view(), name='index'),
]
