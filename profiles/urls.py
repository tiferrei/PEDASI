from django.urls import include, path

app_name = 'profiles'

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
]
