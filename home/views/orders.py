from django.shortcuts import render
from senior_project.utils import login_required
from home.models import Order


@login_required
def order_list(request):
	orders = Order.get_users_orders(request.user)
	return render(request, 'home/orders/list.html', {'orders': orders})


@login_required
def order_confirmation(request, order_uuid):
	return render(request, 'home/orders/confirmation.html')
