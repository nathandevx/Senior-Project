from django.shortcuts import render
from senior_project.utils import login_required


@login_required
def order_list(request):
	return render(request, 'home/orders/list.html')


@login_required
def order_confirmation(request):
	return render(request, 'home/orders/confirmation.html')
