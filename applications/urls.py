from django.urls import path

from . import views

app_name = 'applications'

urlpatterns = [
    path('',
         views.ApplicationListView.as_view(),
         name='application.list'),

    path('create/',
         views.ApplicationCreateView.as_view(),
         name='application.create'),

    path('<int:pk>/',
         views.ApplicationDetailView.as_view(),
         name='application.detail'),

    path('<int:pk>/update',
         views.ApplicationUpdateView.as_view(),
         name='application.update'),

    path('<int:pk>/delete',
         views.ApplicationDeleteView.as_view(),
         name='application.delete'),
]
