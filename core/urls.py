from django.conf import settings

from rest_framework import routers


class APIRootRouter(routers.SimpleRouter):
    """
    API Router to allow all API components to be kept under a single root URL (/api).

    Registered routes are added to a shared router which can then be queried to get the full URL scheme.
    """
    shared_router = routers.DefaultRouter()

    def register(self, *args, **kwargs):
        self.shared_router.register(*args, **kwargs)
        super().register(*args, **kwargs)


def api_urls():
    """
    Get all API URL scheme components registered with :class:`APIRootRouter`.

    To ensure that all API components are registered, attempt to import the URL module of each Django app.

    :return: API URL scheme to be included in Django URLs
    """
    from importlib import import_module

    for app in settings.CUSTOM_APPS:
        try:
            import_module(app + '.urls')
        except (ImportError, AttributeError):
            pass

    return APIRootRouter.shared_router.urls

