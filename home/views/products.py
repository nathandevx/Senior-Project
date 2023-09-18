from django.shortcuts import render
from django.http import HttpResponseForbidden


def product_create(request):
	if not request.user.is_superuser:
		return HttpResponseForbidden()
	return render(request, 'home/products/create.html')


def product_read(request):
	return render(request, 'home/products/read.html')


def product_update(request):
	if not request.user.is_superuser:
		return HttpResponseForbidden()
	return render(request, 'home/products/update.html')


def product_delete(request):
	if not request.user.is_superuser:
		return HttpResponseForbidden()
	return render(request, 'home/products/delete.html')
