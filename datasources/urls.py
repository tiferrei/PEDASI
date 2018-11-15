from django.urls import path

from . import views

app_name = 'datasources'

urlpatterns = [
    path('',
         views.datasource.DataSourceListView.as_view(),
         name='datasource.list'),

    path('<int:pk>/',
         views.datasource.DataSourceDetailView.as_view(),
         name='datasource.detail'),

    path('<int:pk>/audit',
         views.datasource.DataSourceAuditView.as_view(),
         name='datasource.audit'),

    path('<int:pk>/query',
         views.datasource.DataSourceQueryView.as_view(),
         name='datasource.query'),

    path('<int:pk>/metadata',
         views.datasource.DataSourceMetadataView.as_view(),
         name='datasource.metadata'),

    path('<int:pk>/explore',
         views.datasource.DataSourceExploreView.as_view(),
         name='datasource.explore'),

    path('<int:pk>/search',
         views.datasource.DataSourceDataSetSearchView.as_view(),
         name='datasource.dataset.search'),

    #######################
    # Permission management

    path('<int:pk>/access',
         views.user_permission_link.DataSourceAccessManageView.as_view(),
         name='datasource.access.manage'),

    path('<int:pk>/access/request',
         views.user_permission_link.DataSourceAccessRequestView.as_view(),
         name='datasource.access.request'),

    path('<int:pk>/access/grant',
         views.user_permission_link.DataSourceAccessGrantView.as_view(),
         name='datasource.access.grant'),
]
