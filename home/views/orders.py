from django.shortcuts import render


def order_list(request):
	return render(request, 'home/orders/list.html')


def order_confirmation(request):
	return render(request, 'home/orders/confirmation.html')
