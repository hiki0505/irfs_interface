from django.contrib import admin
from .models import Ifrs, DatabaseCredentials, Plist, LGD, LGD_DF, PD_UPD, STAGING

admin.site.register(Ifrs)
admin.site.register(DatabaseCredentials)
admin.site.register(Plist)
admin.site.register(LGD)
admin.site.register(LGD_DF)
admin.site.register(PD_UPD)
admin.site.register(STAGING)
# Register your models here.
