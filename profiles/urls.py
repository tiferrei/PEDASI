from django.urls import include, path

from .views.views import UserInactiveView, UserProfileView, UserUriView

app_name = 'profiles'

urlpatterns = [
    path('profile',
         UserProfileView.as_view(),
         name='profile'),

    path('inactive',
         UserInactiveView.as_view(),
         name='inactive'),

    path('uri/<int:pk>',
         UserUriView.as_view(),
         name='uri'),
]
