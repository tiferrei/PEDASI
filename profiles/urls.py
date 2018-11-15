from django.urls import include, path

from . import views

app_name = 'profiles'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),

    path('profile',
         views.user.UserProfileView.as_view(),
         name='profile'),

    path('inactive',
         views.user.UserInactiveView.as_view(),
         name='inactive'),

    path('uri/<int:pk>',
         views.user.UserUriView.as_view(),
         name='uri'),

    path('orgunit/<int:pk>',
         views.organisational_unit.OrganisationalUnitDetailView.as_view(),
         name='org_unit.detail'),
]
