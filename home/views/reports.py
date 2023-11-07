from django.shortcuts import render
from django.core.mail import send_mail
from django.http import HttpResponse
from senior_project.utils import superuser_required
from home.models import Order
import boto3
import stripe
import environ

env = environ.Env(
	# set casting, default value
	DEBUG=(bool, False)
)


@superuser_required
def report_list(request):
	return render(request, 'home/reports/list.html')


@superuser_required
def report_orders(request):
	return render(request, 'home/reports/orders.html')


@superuser_required
def report_products(request):
	return render(request, 'home/reports/products.html')


@superuser_required
def report_charts(request):
	return render(request, 'home/reports/charts.html')


@superuser_required
def update_total_orders_chart_data(request):
	return HttpResponse("Got orders data")


@superuser_required
def update_total_users_chart_data(request):
	return HttpResponse("Got users data")


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
		print(f"Error with AWS S3: {e}")

	# Check Stripe
	try:
		# Retrieve balance (a simple call to check if API is up and running)
		stripe.Balance.retrieve()
		context['stripe'] = True
	except Exception as e:
		print(f"Error with Stripe: {e}")

	# Check SendGrid
	try:
		send_mail(
			'SendGrid SMTP Test',
			'Testing SendGrid SMTP as requested.',
			env('FROM_EMAIL'),
			[env('ADMIN_EMAIL')],
			fail_silently=False,
		)  # todo these email
		context['sendgrid'] = True
	except Exception as e:
		print(f"Error with SendGrid: {e}")

	return render(request, 'home/reports/api_status.html', context)
