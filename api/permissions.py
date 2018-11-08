from rest_framework import permissions

from datasources import models


# TODO make permission class factory
# TODO write permission tests

class MetadataPermission(permissions.BasePermission):
    message = 'You do not have permission to access the metadata of this resource.'

    def has_object_permission(self, request, view, obj):
        permission = models.UserPermissionLink.objects.get(
            user=request.user,
            datasource=obj
        )

        return permission.granted >= models.UserPermissionLevels.META


class DataPermission(permissions.BasePermission):
    message = 'You do not have permission to access the data of this resource.'

    def has_object_permission(self, request, view, obj):
        permission = models.UserPermissionLink.objects.get(
            user=request.user,
            datasource=obj
        )

        return permission.granted >= models.UserPermissionLevels.DATA


class ProvPermission(permissions.BasePermission):
    message = 'You do not have permission to access the prov data of this resource.'

    def has_object_permission(self, request, view, obj):
        permission = models.UserPermissionLink.objects.get(
            user=request.user,
            datasource=obj
        )

        return permission.granted >= models.UserPermissionLevels.PROV
