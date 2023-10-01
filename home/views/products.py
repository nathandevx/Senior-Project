from django.shortcuts import render
from django.http import HttpResponseForbidden
from senior_project.utils import superuser_required


@superuser_required
def product_create(request):
	return render(request, 'home/products/create.html')


def product_read(request):
	return render(request, 'home/products/read.html')


@superuser_required
def product_update(request):
	return render(request, 'home/products/update.html')


@superuser_required
def product_delete(request):
	return render(request, 'home/products/delete.html')
