from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from interface import views

from interface.views import DatabaseLogin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/logindb', DatabaseLogin.as_view()),
]
