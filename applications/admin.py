from django.contrib import admin

from . import models


class ApplicationAdmin(admin.ModelAdmin):
    pass


admin.site.register(models.Application, ApplicationAdmin)
