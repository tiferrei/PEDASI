from django.contrib import admin

from . import models


class DataSourceAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None) -> bool:
        """
        Does the user have permission to change this object?
        """
        permission = super().has_change_permission(request, obj)

        if obj is not None:
            permission &= obj.owner == request.user

        return permission


admin.site.register(models.DataSource, DataSourceAdmin)
