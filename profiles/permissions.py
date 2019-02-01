from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin


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
        return self.request.user.is_superuser or (
                super().has_permission() and
                self.request.user == getattr(self.get_object(), self.owner_attribute)
        )


class HasViewPermissionMixin(UserPassesTestMixin):
    """
    Mixin to reject users who do not have permission to view this DataSource.
    """
    def test_func(self) -> bool:
        return self.get_object().has_view_permission(self.request.user)
