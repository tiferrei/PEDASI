from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models


admin.site.register(models.User, UserAdmin)


@admin.register(models.Institution)
class InstitutionAdmin(admin.ModelAdmin):
    pass
