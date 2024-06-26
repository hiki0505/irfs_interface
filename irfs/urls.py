from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from interface import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url('^$', views.homepage, name='homepage'),
    url('general', views.general, name='general'),
    url('predict', views.predictMPG, name='predictMPG'),
    url('connect', views.connect, name='connect'),
    url('dbconn_view', views.dbconn_view, name='dbconn_view')
]
