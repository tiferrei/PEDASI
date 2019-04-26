"""
Permission check classes to be used with djangorestframework API.
"""

from rest_framework import permissions

from datasources import models


class BaseUserPermission(permissions.BasePermission):
    """
    Base permission check.  Permissions should override the `permission_level` property.
    """
    message = 'You do not have permission to access this resource.'
    permission_level = models.UserPermissionLevels.NONE

    def has_object_permission(self, request, view, obj):
        return obj.has_permission_level(request.user, self.permission_level)


class ViewPermission(BaseUserPermission):
    """
    Assert that a user has the :class:`models.UserPermissionLevels.VIEW` permission.
    """
    message = 'You do not have permission to access this resource.'
    permission_level = models.UserPermissionLevels.VIEW


class MetadataPermission(BaseUserPermission):
    """
    Assert that a user has the :class:`models.UserPermissionLevels.META` permission.
    """
    message = 'You do not have permission to access the metadata of this resource.'
    permission_level = models.UserPermissionLevels.META


class DataPermission(BaseUserPermission):
    """
    Assert that a user has the :class:`models.UserPermissionLevels.DATA` permission.
    """
    message = 'You do not have permission to access the data of this resource.'
    permission_level = models.UserPermissionLevels.DATA


class ProvPermission(BaseUserPermission):
    """
    Assert that a user has the :class:`models.UserPermissionLevels.PROV` permission.
    """
    message = 'You do not have permission to access the prov data of this resource.'
    permission_level = models.UserPermissionLevels.PROV


class DataPushPermission(permissions.BasePermission):
    """
    Permission mixin to prevent access to POST and PUT methods by users who do not have the correct permission flag.
    """
    message = 'You do not have permission to push data to this resource.'

    def has_object_permission(self, request, view, obj):
        # Bypass if not pushing data
        if request.method not in {'POST', 'PUT'}:
            return True

        # Owner always has permission
        if request.user == obj.owner:
            return True

        try:
            permission = models.UserPermissionLink.objects.get(
                user=request.user,
                datasource=obj
            )

            return permission.push_granted

        except models.UserPermissionLink.DoesNotExist:
            # Permission must have been granted explicitly
            return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Grant admins write access - all others get read-only.
    """
    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS or
            request.user.is_superuser
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Grant owner and admins write access - all others get read-only.
    """
    message = 'You do not have permission to access this resource.'

    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS or
            view.get_datasource().owner == request.user or
            request.user.is_superuser
        )
