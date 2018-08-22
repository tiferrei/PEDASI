from django.contrib import admin

from . import models


@admin.register(models.DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    readonly_fields = ['owner']

    def has_change_permission(self, request, obj=None) -> bool:
        """
        Does the user have permission to change this object?
        """
        permission = super().has_change_permission(request, obj)

        if obj is not None:
            permission &= obj.owner == request.user

        return permission

    def has_delete_permission(self, request, obj=None) -> bool:
        """
        Does the user have permission to delete this object?
        """
        permission = super().has_delete_permission(request, obj)

        if obj is not None:
            permission &= obj.owner == request.user

        return permission

    def save_model(self, request, obj, form, change):
        """
        Set missing fields when model is saved.
        """
        try:
            owner = form.instance.owner
        except models.DataSource.owner.RelatedObjectDoesNotExist:
            form.instance.owner = request.user

        super().save_model(request, obj, form, change)
