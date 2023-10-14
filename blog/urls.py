from django.urls import path
from blog import views
from django.urls import path

app_name = 'blog'
urlpatterns = [
	path('posts/', views.post_list, name='post-list'),
	path('post/create/', views.post_create, name='post-create'),
	path('post/<int:pk>/', views.post_read, name='post-read'),
	path('post/update/<int:pk>/', views.post_update, name='post-update'),
	path('post/delete/<int:pk>/', views.post_delete, name='post-delete'),

]

from . import views
urlpatterns = [
    # ... Your other URL patterns

    path('export/user_counts/<int:year>/', views.export_user_counts_to_csv, name='export_user_counts'),
    path('export/years_with_users/', views.export_years_with_users_to_csv, name='export_years_with_users'),
]
