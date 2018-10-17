from django.urls import path

from . import views

app_name = 'datasources'

urlpatterns = [
    path('',
         views.DataSourceListView.as_view(),
         name='datasource.list'),

    path('<int:pk>/',
         views.DataSourceDetailView.as_view(),
         name='datasource.detail'),

    path('<int:pk>/manage-access',
         views.DataSourceManageAccessView.as_view(),
         name='datasource.manage-access'),

    path('<int:pk>/users/<int:user_pk>',
         views.DataSourceRequestAccessView.as_view(),
         name='datasource.manage-access.user'),

    path('<int:pk>/query',
         views.DataSourceQueryView.as_view(),
         name='datasource.query'),

    path('<int:pk>/metadata',
         views.DataSourceMetadataView.as_view(),
         name='datasource.metadata'),

    path('<int:pk>/explore',
         views.DataSourceExploreView.as_view(),
         name='datasource.explore'),
]
