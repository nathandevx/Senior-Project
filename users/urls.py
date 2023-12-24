from django.urls import path
from users import views

app_name = 'users'
urlpatterns = [
	path('login/', views.CustomLoginView.as_view(), name='account_login'),
	path('profile/', views.profile, name='profile'),
	path('delete-account/', views.delete_user, name='delete-user'),
	path('login-as-admin/', views.login_as_admin, name='login-as-admin'),
	path('login-as-customer/', views.login_as_customer, name='login-as-customer'),
]
