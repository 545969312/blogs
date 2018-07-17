"""Blogs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path
from blog import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('suggest/', views.suggest, name='suggest'),
    path('comment/', views.comment, name='comment'),

    path('code/', views.code, name='code'),

    path('query_article/', views.query_article, name='query_article'),
    path('add_article/', views.add_article, name='add_article'),
    path('upload/', views.upload, name='upload'),
    path('upload_img/', views.upload_img, name='upload_img'),

    re_path('change_article/(?P<change_id>\d+)/$', views.change_article),

    re_path('(?P<username>\w+)/(?P<condition>category|tag|archives)/(?P<param>.*)/$', views.homesite),
    re_path('(?P<condition>category|tag|archives)/(?P<param>.*)/$', views.index),

    re_path('(?P<username>\w+)/article_content_site/(?P<article_id>\d+)/$', views.article_content_site),
    re_path('article_content/(?P<article_id>\d+)/$', views.article_content),

    re_path('(?P<username>\w+)/$', views.homesite, name='homesite'),

    re_path('del_article/(?P<dele>\d+)', views.del_article),

]
