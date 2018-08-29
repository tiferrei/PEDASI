from django.urls import include, path

from .views.views import UserProfileView

app_name = 'profiles'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),

    path('profile',
         UserProfileView.as_view(),
         name='profile'),
]
