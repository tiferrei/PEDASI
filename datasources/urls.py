from django.urls import path

from . import views

app_name = 'datasources'

urlpatterns = [
    path('',
         views.datasource.DataSourceListView.as_view(),
         name='datasource.list'),

    path('add',
         views.datasource.DataSourceCreateView.as_view(),
         name='datasource.add'),

    path('<int:pk>/',
         views.datasource.DataSourceDetailView.as_view(),
         name='datasource.detail'),

    path('<int:pk>/edit',
         views.datasource.DataSourceUpdateView.as_view(),
         name='datasource.edit'),

    path('<int:pk>/delete',
         views.datasource.DataSourceDeleteView.as_view(),
         name='datasource.delete'),

    path('<int:pk>/metadata',
         views.datasource.DataSourceMetadataView.as_view(),
         name='datasource.metadata'),

    path('<int:pk>/explorer',
         views.datasource.DataSourceExplorerView.as_view(),
         name='datasource.explorer'),

    path('<int:pk>/search',
         views.datasource.DataSourceDataSetSearchView.as_view(),
         name='datasource.dataset.search'),

    ##########
    # Licences

    path('licences',
         views.licence.LicenceListView.as_view(),
         name='licence.list'),

    path('licences/add',
         views.licence.LicenceCreateView.as_view(),
         name='licence.add'),

    path('licences/<int:pk>/',
         views.licence.LicenceDetailView.as_view(),
         name='licence.detail'),

    path('licences/<int:pk>/edit',
         views.licence.LicenceUpdateView.as_view(),
         name='licence.edit'),

    path('licences/<int:pk>/delete',
         views.licence.LicenceDeleteView.as_view(),
         name='licence.delete'),

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
