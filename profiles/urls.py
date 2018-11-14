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

    path('institutions/<int:pk>',
         views.institution.InstitutionDetailView.as_view(),
         name='institution.detail'),
]
