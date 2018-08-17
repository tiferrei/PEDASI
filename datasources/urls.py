from django.urls import path

from . import views

app_name = 'datasources'

urlpatterns = [
    path('',
         views.DataSourceListView.as_view(),
         name='datasource.list'),

    path('create/',
         views.DataSourceCreateView.as_view(),
         name='datasource.create'),

    path('<int:pk>/',
         views.DataSourceDetailView.as_view(),
         name='datasource.detail'),

    path('<int:pk>/update',
         views.DataSourceUpdateView.as_view(),
         name='datasource.update'),

    path('<int:pk>/delete',
         views.DataSourceDeleteView.as_view(),
         name='datasource.delete'),
]
