from django.urls import path
from blog import views

app_name = 'blog'
urlpatterns = [
	path('posts/', views.post_list, name='post-list'),
	path('post/create/', views.post_create, name='post-create'),
	path('post/<int:pk>/', views.post_read, name='post-read'),
	path('post/update/<int:pk>/', views.post_update, name='post-update'),
	path('post/delete/<int:pk>/', views.post_delete, name='post-delete'),
]
