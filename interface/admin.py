from django.contrib import admin
from .models import Ifrs, DatabaseCredentials, Plist

admin.site.register(Ifrs)
admin.site.register(DatabaseCredentials)
admin.site.register(Plist)

# Register your models here.
