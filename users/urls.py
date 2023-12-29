from django.urls import path
from users import views

app_name = 'users'
urlpatterns = [
	path('login/', views.CustomLoginView.as_view(), name='account_login'),
	path('profile/', views.profile, name='profile'),
	path('delete-account/', views.delete_user, name='delete-user'),
	path('login-as-admin/', views.login_as_admin, name='login-as-admin'),
	path('login-as-customer/', views.login_as_customer, name='login-as-customer'),
	path('login-as-superuser/', views.login_as_superuser, name='login-as-superuser'),

	# Overrides django-allauth views
	path('email/', views.custom_email_change, name='account_email'),
	path('password/change/', views.custom_password_change, name='account_change_password'),
	path('password/reset/', views.custom_password_reset, name='account_reset_password'),
]
