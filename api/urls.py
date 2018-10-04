from django.urls import include, path

from rest_framework import routers

from .views import datasources as datasource_views

app_name = 'api'

# Register ViewSets
router = routers.DefaultRouter()
router.register('datasources', datasource_views.DataSourceApiViewset)
router.register('datasources', datasource_views.DataSourceMetadataListApiView)

urlpatterns = [
    path('',
         include(router.urls)),
]
