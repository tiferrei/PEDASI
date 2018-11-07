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

    path('<int:pk>/access',
         views.DataSourceAccessManageView.as_view(),
         name='datasource.access.manage'),

    # Requires level to be provided as kwargs
    path('<int:pk>/access/request',
         views.DataSourceAccessRequestView.as_view(),
         name='datasource.access.request'),

    # Requires user and level to be provided as kwargs
    path('<int:pk>/access/grant',
         views.DataSourceAccessGrantView.as_view(),
         name='datasource.access.grant'),

    path('<int:pk>/query',
         views.DataSourceQueryView.as_view(),
         name='datasource.query'),

    path('<int:pk>/metadata',
         views.DataSourceMetadataView.as_view(),
         name='datasource.metadata'),

    path('<int:pk>/explore',
         views.DataSourceExploreView.as_view(),
         name='datasource.explore'),

    path('<int:pk>/search',
         views.DataSourceDataSetSearchView.as_view(),
         name='datasource.dataset.search'),
]
