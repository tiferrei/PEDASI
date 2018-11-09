from rest_framework import permissions

from datasources import models


# TODO make permission class factory
# TODO write permission tests

class ViewPermission(permissions.BasePermission):
    message = 'You do not have permission to access this resource.'

    def has_object_permission(self, request, view, obj):
        if not obj.access_control:
            return True

        try:
            permission = models.UserPermissionLink.objects.get(
                user=request.user,
                datasource=obj
            )

            return permission.granted >= models.UserPermissionLevels.VIEW

        except models.UserPermissionLink.DoesNotExist:
            return False


class MetadataPermission(permissions.BasePermission):
    message = 'You do not have permission to access the metadata of this resource.'

    def has_object_permission(self, request, view, obj):
        if not obj.access_control:
            return True

        try:
            permission = models.UserPermissionLink.objects.get(
                user=request.user,
                datasource=obj
            )

            return permission.granted >= models.UserPermissionLevels.META

        except models.UserPermissionLink.DoesNotExist:
            return False


class DataPermission(permissions.BasePermission):
    message = 'You do not have permission to access the data of this resource.'

    def has_object_permission(self, request, view, obj):
        if not obj.access_control:
            return True

        try:
            permission = models.UserPermissionLink.objects.get(
                user=request.user,
                datasource=obj
            )

            return permission.granted >= models.UserPermissionLevels.DATA

        except models.UserPermissionLink.DoesNotExist:
            return False


class ProvPermission(permissions.BasePermission):
    message = 'You do not have permission to access the prov data of this resource.'

    def has_object_permission(self, request, view, obj):
        if not obj.access_control:
            return True

        try:
            permission = models.UserPermissionLink.objects.get(
                user=request.user,
                datasource=obj
            )

            return permission.granted >= models.UserPermissionLevels.PROV

        except models.UserPermissionLink.DoesNotExist:
            return False
