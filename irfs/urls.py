from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from interface import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url('^$', views.index, name='homepage'),
    url('predictMPG', views.predictMPG, name='predictMPG')
]
