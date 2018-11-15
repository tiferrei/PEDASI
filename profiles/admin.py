from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models


class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('organisational_unit',)

    fieldsets = (
        (None,
            {'fields': ('username', 'password')}),
        ('Personal info',
            {'fields': ('first_name', 'last_name', 'email', 'organisational_unit')}),
        ('Permissions',
            {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_auditor', 'is_superauditor', 'groups', 'user_permissions')}),
        ('Important dates',
            {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(models.User, CustomUserAdmin)


@admin.register(models.OrganisationalUnit)
class OrganisationalUnitAdmin(admin.ModelAdmin):
    pass
