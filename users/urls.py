from django.urls import path
from users import views

app_name = 'users'
urlpatterns = [
	path('profile/', views.profile, name='profile'),
	path('delete-account/', views.delete_user, name='delete-user'),
]
