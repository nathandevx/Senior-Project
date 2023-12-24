from django.shortcuts import render
from django.utils import timezone
from django.core.mail import send_mail
from django.db.models.functions import TruncDate
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from senior_project.utils import superuser_required, get_table_data
from home.models import Product, Order
from blog.models import Post
import json
import boto3
import stripe
import environ

env = environ.Env(
	# set casting, default value
	DEBUG=(bool, False)
)

User = get_user_model()


@superuser_required
def report_list(request):
	return render(request, 'home/reports/list.html')


@superuser_required
def report_orders(request):
	data = get_table_data(request, Order)
	return render(request, 'home/reports/orders.html', {'orders': data[0], 'order_by': data[1], 'order_model': Order})


@superuser_required
def report_products(request):
	data = get_table_data(request, Product)
	return render(request, 'home/reports/products.html', {'products': data[0], 'order_by': data[1], 'product_model': Product})


@superuser_required
def report_blogs(request):
	data = get_table_data(request, Post)
	return render(request, 'home/reports/blogs.html', {'posts': data[0], 'order_by': data[1], 'post_model': Post})


@superuser_required
def report_charts(request):
	current_year = timezone.now().year

	orders_by_date = Order.objects.annotate(date_only=TruncDate('created_at')).values('date_only').annotate(
		order_count=Count('id')).order_by('date_only')

	# dates = [obj['date_only'] for obj in orders_by_date]
	dates = [order['date_only'].strftime('%Y-%m-%d') for order in orders_by_date]
	order_counts = [obj['order_count'] for obj in orders_by_date]

	# Total users data
	users = User.get_total_year_users(current_year)
	years_with_users = User.get_years_with_users()

	# Total orders data
	orders = Order.get_year_months_total_orders(current_year)
	years_with_orders = Order.get_years_with_orders()

	# Order status data
	order_statuses = list(Order.get_order_statuses())
	order_statuses_serialized = json.dumps(order_statuses)

	# Top selling products data
	product_names, product_order_counts = Product.get_top_10_selling_products()

	context = {
		'dates': dates,
		'order_counts': order_counts,
		'user_months': users[0],
		'user_data': users[1],
		'order_months': orders[0],
		'order_data': orders[1],
		'years_with_orders': years_with_orders,
		'years_with_users': years_with_users,
		'current_year': current_year,
		'order_statuses': order_statuses_serialized,
		'product_names': product_names,
		'product_order_counts': product_order_counts,
	}
	return render(request, 'home/reports/charts.html', context)


@superuser_required
def update_total_orders_chart_data(request):
	year = request.GET.get('orders_year')
	if year == '---':
		months = None
		months_order_totals = None
	else:
		months, months_order_totals = Order.get_year_months_total_orders(year)
	return JsonResponse({
		'orders_labels': months,
		'orders_values': months_order_totals,
	})


@superuser_required
def update_total_users_chart_data(request):
	year = request.GET.get('users_year')
	if year == '---':
		months = None
		months_user_totals = None
	else:
		months, months_user_totals = User.get_total_year_users(year)
	return JsonResponse({
		'users_labels': months,
		'users_values': months_user_totals,
	})


@superuser_required
def report_export(request):
	return render(request, 'home/reports/export.html')


@superuser_required
def report_export_download(request):
	# Create the HttpResponse object with the appropriate headers for CSV.
	response = HttpResponse(content_type='text/tsv')
	response['Content-Disposition'] = 'attachment; filename="report.tsv"'
	Order.get_export_data(response)
	return response

@superuser_required
def report_api_status(request):
	context = {
		'aws': False,
		'stripe': False,
		'sendgrid': False,
	}

	# Check AWS S3
	try:
		s3 = boto3.client('s3')
		# Here you can do a simple operation like listing the buckets
		s3.list_buckets()
		context['aws'] = True
	except Exception as e:
		pass

	# Check Stripe
	try:
		# Retrieve balance (a simple call to check if API is up and running)
		stripe.Balance.retrieve()
		context['stripe'] = True
	except Exception as e:
		pass

	# Check SendGrid
	try:
		send_mail(
			'SendGrid SMTP Test',
			'Testing SendGrid SMTP as requested.',
			env('ADMIN_EMAIL'),
			[env('ADMIN_EMAIL')],
			fail_silently=False,
		)
		context['sendgrid'] = True
	except Exception as e:
		pass

	return render(request, 'home/reports/api_status.html', context)