from rest_framework import permissions

from datasources import models


class BaseUserPermission(permissions.BasePermission):
    message = 'You do not have permission to access this resource.'
    permission_level = models.UserPermissionLevels.NONE

    def has_object_permission(self, request, view, obj):
        return obj.has_permission_level(request.user, self.permission_level)


class ViewPermission(BaseUserPermission):
    message = 'You do not have permission to access this resource.'
    permission_level = models.UserPermissionLevels.VIEW


class MetadataPermission(BaseUserPermission):
    message = 'You do not have permission to access the metadata of this resource.'
    permission_level = models.UserPermissionLevels.META


class DataPermission(BaseUserPermission):
    message = 'You do not have permission to access the data of this resource.'
    permission_level = models.UserPermissionLevels.DATA


class ProvPermission(BaseUserPermission):
    message = 'You do not have permission to access the prov data of this resource.'
    permission_level = models.UserPermissionLevels.PROV
