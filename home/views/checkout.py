from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from home.models import Product, Cart
from home.forms import ShippingAddressForm
from senior_project.utils import login_required, get_allowed_cities
import environ
import stripe

env = environ.Env(
	# set casting, default value
	DEBUG=(bool, False)
)

stripe.api_key = env('STRIPE_SECRET_KEY')


@login_required
def shipping_info(request):
	cart = Cart.get_active_cart_or_create_new_cart(request.user)
	access = cart.not_creator_or_inactive_cart(request.user)
	last_shipping_address = request.user.get_last_shipping_address()
	if access:
		return HttpResponseForbidden()
	if cart.has_errors():
		return render(request, 'home/carts/cart_errors.html', context=cart.has_errors())
	if cart.is_empty():
		return render(request, 'home/carts/cart_empty.html', {'product_model': Product})

	if request.method == 'POST':
		form = ShippingAddressForm(request.POST)
		if form.is_valid():
			shipping_address = form.save(commit=False)
			shipping_address.creator = request.user
			shipping_address.updater = request.user
			shipping_address.save()

			# Update the cart's shipping address
			cart.set_shipping_address(shipping_address)
			return redirect('home:proceed-to-stripe')
	else:
		form = ShippingAddressForm(instance=last_shipping_address)

	context = {
		'form': form,
		'cities': ', '.join(get_allowed_cities()),
	}
	return render(request, 'home/checkout/shipping_info.html', context)


@login_required
def proceed_to_stripe(request):
	cart = Cart.get_active_cart_or_create_new_cart(request.user)

	access = cart.not_creator_or_inactive_cart(request.user)
	if access:
		return HttpResponseForbidden()
	if cart.has_errors():
		return render(request, 'home/carts/cart_errors.html', context=cart.has_errors())
	if cart.is_empty():
		return render(request, 'home/carts/cart_empty.html', {'product_model': Product})

	# Shipping address required to continue
	if not cart.shipping_address:
		return render(request, 'home/checkout/no_shipping_info.html')

	if request.method == 'POST':
		checkout_session_url = cart.create_stripe_checkout_session()
		return redirect(checkout_session_url, code=303)
	else:
		return render(request, 'home/checkout/proceed_to_stripe.html')


@login_required
def payment_success(request, cart_uuid):
	cart = get_object_or_404(Cart, uuid=cart_uuid)
	access = cart.not_creator_or_inactive_cart(request.user)
	if access:
		return HttpResponseForbidden()
	if cart.has_order():  # they already ordered, don't let them order again
		return HttpResponseForbidden()
	order = cart.create_order()
	cart.handle_cart_purchase(request, order)
	cart.set_original_price_for_all_cart_items()
	order.send_order_confirmation_email()
	cart.set_cart_as_inactive(request.user)
	Cart.get_active_cart_or_create_new_cart(request.user)
	if request.user.is_demo_account:
		messages.info(request, 'You will not receive an order confirmation email because you are using a demo account.')
	return redirect(order.get_read_url())


@login_required
def payment_cancel(request):
	return render(request, 'home/checkout/payment_cancel.html')
