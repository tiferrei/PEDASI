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

    path('<int:pk>/delete',
         views.ApplicationDeleteView.as_view(),
         name='application.delete'),

    path('<int:pk>/token',
         views.ApplicationGetTokenView.as_view(),
         name='token'),

    path('<int:pk>/token',
         views.ApplicationGetTokenView.as_view(),
         name='token'),

    path('<int:pk>/manage-access',
         views.ApplicationManageAccessView.as_view(),
         name='application.manage-access'),

    path('<int:pk>/manage-access/users/<int:user_pk>',
         views.ApplicationManageAccessView.as_view(),
         name='application.manage-access.user'),
]
