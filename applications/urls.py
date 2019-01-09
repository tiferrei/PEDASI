from django.urls import path

from . import views

app_name = 'applications'

urlpatterns = [
    path('',
         views.ApplicationListView.as_view(),
         name='application.list'),

    path('add',
         views.ApplicationCreateView.as_view(),
         name='application.add'),

    path('<int:pk>/',
         views.ApplicationDetailView.as_view(),
         name='application.detail'),

    path('<int:pk>/edit',
         views.ApplicationUpdateView.as_view(),
         name='application.edit'),

    path('<int:pk>/manage-access',
         views.ApplicationManageAccessView.as_view(),
         name='application.manage-access'),

    path('<int:pk>/manage-access/users/<int:user_pk>',
         views.ApplicationManageAccessView.as_view(),
         name='application.manage-access.user'),
]
