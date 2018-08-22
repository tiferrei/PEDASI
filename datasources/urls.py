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
]
