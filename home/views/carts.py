from django.shortcuts import render
from django.http import HttpResponseForbidden


def cart_read(request):
	return render(request, 'home/carts/read.html')


def cart_delete(request):
	return render(request, 'home/carts/delete.html')
