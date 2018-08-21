from django.urls import path

from . import views

app_name = 'applications'

urlpatterns = [
    path('',
         views.ApplicationListView.as_view(),
         name='application.list'),

    path('<int:pk>/',
         views.ApplicationDetailView.as_view(),
         name='application.detail'),
]
