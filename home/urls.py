from django.urls import path
from home import views

app_name = 'home'
urlpatterns = [
	path('about/', views.about, name='about'),
	path('blog/', views.blog, name='blog'),
	path('contact/', views.contact, name='contact'),
	path('', views.home, name='home'),
	path('order/', views.order, name='order'),
	path('product/', views.product, name='product'),
	path('report/', views.report, name='report'),
]
