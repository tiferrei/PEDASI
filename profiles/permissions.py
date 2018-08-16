from django.contrib.auth.mixins import PermissionRequiredMixin


class OwnerPermissionRequiredMixin(PermissionRequiredMixin):
    """
    Mixin to require that a user has the relevant global permission and is the owner of the relevant object.

    TODO replace this with 'django-guardian' once it supports Django 2.1 or use 'rules'
    """
    owner_attribute = 'owner'

    def has_permission(self) -> bool:
        """
        Require the the user has the relevant global permission and is the owner of this object.

        :return: Does the user have permission to perform this action?
        """
        return super().has_permission() and self.request.user == getattr(self.get_object(), self.owner_attribute)
