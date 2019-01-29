from django.contrib.auth.mixins import UserPassesTestMixin


class OwnerPermissionMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user == self.get_object().owner or self.request.user.is_superuser
