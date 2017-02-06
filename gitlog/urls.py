from django.conf.urls import url
from . import views

urlpatterns = [
 #       url(r'^$', views.IndexView.as_view(), name='index'),
        url(r'^getlog/$', views.GetloglView.as_view(), name='getlog'),
        url(r'^updatelog/$', views.Updatelog, name='updatelog'),
#      url(r'^pubsites/$', views.Pubsites, name='pubsites'),
]