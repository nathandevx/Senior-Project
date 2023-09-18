from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponse


def report_list(request):
	if not request.user.is_superuser:
		return HttpResponseForbidden()
	return render(request, 'home/reports/list.html')


def report_orders(request):
	if not request.user.is_superuser:
		return HttpResponseForbidden()
	return render(request, 'home/reports/orders.html')


def report_products(request):
	if not request.user.is_superuser:
		return HttpResponseForbidden()
	return render(request, 'home/reports/products.html')


def report_charts(request):
	if not request.user.is_superuser:
		return HttpResponseForbidden()
	return render(request, 'home/reports/charts.html')


def update_total_orders_chart_data(request):
	if not request.user.is_superuser:
		return HttpResponseForbidden()
	return HttpResponse("Got orders data")


def update_total_users_chart_data(request):
	if not request.user.is_superuser:
		return HttpResponseForbidden()
	return HttpResponse("Got users data")


def report_export(request):
	if not request.user.is_superuser:
		return HttpResponseForbidden()
	return render(request, 'home/reports/export.html')


def report_export_download(request):
	if not request.user.is_superuser:
		return HttpResponseForbidden()
	return HttpResponse("Downloaded")


def report_api_status(request):
	if not request.user.is_superuser:
		return HttpResponseForbidden()
	return render(request, 'home/reports/api_status.html')
