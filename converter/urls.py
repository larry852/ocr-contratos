from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<document>[\d]+)', views.index, name='index'),
    url(r'^$', views.index, name='index'),
]
