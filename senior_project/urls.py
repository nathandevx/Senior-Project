from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('home.urls')),
    path('accounts/', include('users.urls')),
    path('accounts/', include('allauth.urls')),
    path("admin/", admin.site.urls),  # low - change this to something else in production to avoid bots trying to brute force it
]
