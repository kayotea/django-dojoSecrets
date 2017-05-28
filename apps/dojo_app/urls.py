from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^register/process$', views.register_process),
    url(r'^login$', views.login),
    url(r'^secrets$', views.secrets),
    url(r'^delete/(?P<id>\d+)$', views.delete),
    url(r'^post/secret$', views.post_secret),
    url(r'^like/post/(?P<id>\d+)$', views.like),
    url(r'^delete/(?P<id>\d+)$', views.delete),
    url(r'^popular$', views.popular)
]