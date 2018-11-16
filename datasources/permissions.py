from django.contrib.auth.mixins import UserPassesTestMixin


class HasPermissionLevelMixin(UserPassesTestMixin):
    """
    Mixin to reject users who do not have permission to view this DataSource.
    """
    #: Required permission level from datasources.models.UserPermissionLevels
    permission_level = None

    def test_func(self) -> bool:
        return self.get_object().has_permission_level(self.request.user, self.permission_level)
