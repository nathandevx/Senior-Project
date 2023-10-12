from django.urls import path
from home.views import views, products, carts, checkout, orders, reports

app_name = 'home'
urlpatterns = [
	path('', views.home, name='home'),
	path('about/', views.about, name='about'),
	path('contact/', views.contact, name='contact'),

	# Products
	path('product/', views.product, name='product'),
	path('product/create/', products.product_create, name='product-create'),
	path('product/<int:pk>/', products.product_read, name='product-read'),
	path('product/update/<int:pk>/', products.product_update, name='product-update'),
	path('product/delete/<int:pk>/', products.product_delete, name='product-delete'),

	# Carts
	path('cart/<int:pk>/', carts.cart_read, name='cart-read'),  # also acts as cart/update/
	path('cart/delete/<int:pk>/', carts.cart_delete, name='cart-delete'),
	path('cart-demo/', views.cart_demo, name='cart-demo'),

	# Checkout
	path('checkout/shipping-info/', checkout.shipping_info, name='shipping-info'),
	path('checkout/proceed-to-stripe/', checkout.proceed_to_stripe, name='proceed-to-stripe'),
	path('checkout/payment-success/<uuid:cart_uuid>/', checkout.payment_success, name='payment-success'),
	path('checkout/payment-cancel/', checkout.payment_cancel, name='payment-cancel'),
	path('checkout/stripe-test/', checkout.stripe_test, name='stripe-test'),

	# Orders
	path('order', views.order, name='order'),
	path('order/list/', orders.order_list, name='order-list'),
	path('order-confirmation/<uuid:order_uuid>/', orders.order_confirmation, name='order-confirmation'),

	# Reports
	path('report/', views.report, name='report'),
	path('report/list/', reports.report_list, name='report-list'),
	path('report/orders/', reports.report_orders, name='report-orders'),
	path('report/products/', reports.report_products, name='report-products'),
	path('report/charts/', reports.report_charts, name='report-charts'),
	path('report/order-total/update-chart-data/', reports.update_total_orders_chart_data, name='report-update-total-orders-chart-data'),
	path('report/user-total/update-user-data/', reports.update_total_users_chart_data, name='report-update-total-users-chart-data'),
	path('report/export/', reports.report_export, name='report-export'),
	path('report/export/download/', reports.report_export_download, name='report-export-download'),
	path('report/api-status/', reports.report_api_status, name='report-api-status'),
]
