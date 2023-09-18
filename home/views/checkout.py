from django.shortcuts import render
from django.http import HttpResponseForbidden


def shipping_info(request):
	return render(request, 'home/checkout/shipping_info.html')


def proceed_to_stripe(request):
	return render(request, 'home/checkout/proceed_to_stripe.html')


def payment_success(request):
	return render(request, 'home/checkout/payment_success.html')


def payment_cancel(request):
	return render(request, 'home/checkout/payment_cancel.html')