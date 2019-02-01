from django.urls import include, path

from . import views

app_name = 'profiles'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),

    path('profile',
         views.UserProfileView.as_view(),
         name='profile'),

    path('inactive',
         views.UserInactiveView.as_view(),
         name='inactive'),

    path('uri/<int:pk>',
         views.UserUriView.as_view(),
         name='uri'),

    path('token',
         views.UserGetTokenView.as_view(),
         name='token'),
]
