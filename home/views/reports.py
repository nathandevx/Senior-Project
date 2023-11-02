from django.shortcuts import render
from django.http import HttpResponse
from senior_project.utils import superuser_required, get_table_data
from home.models import Product, Order
from blog.models import Post


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
	return render(request, 'home/reports/api_status.html')
