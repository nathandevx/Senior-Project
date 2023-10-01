from django.shortcuts import render
from django.http import HttpResponseForbidden
from senior_project.utils import login_required


@login_required
def cart_read(request):
	return render(request, 'home/carts/read.html')


@login_required
def cart_delete(request):
	return render(request, 'home/carts/delete.html')
