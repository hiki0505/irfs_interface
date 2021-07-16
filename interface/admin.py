from django.contrib import admin
from .models import Ifrs, DatabaseCredentials

admin.site.register(Ifrs)
admin.site.register(DatabaseCredentials)
# Register your models here.
