from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse
from senior_project.utils import superuser_required


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
	return HttpResponse("Downloaded")


@superuser_required
def report_api_status(request):
	return render(request, 'home/reports/api_status.html')
