from django.shortcuts import render, redirect
from django.core.files import File
from django.http import HttpResponseForbidden
from home.models import Product, ProductImage, Cart, CartItem
from senior_project.utils import get_random_date, login_required
import environ
import stripe

env = environ.Env(
	# set casting, default value
	DEBUG=(bool, False)
)

stripe.api_key = env('STRIPE_SECRET_KEY')


@login_required
def shipping_info(request):
	return render(request, 'home/checkout/shipping_info.html')


@login_required
def proceed_to_stripe(request):
	return render(request, 'home/checkout/proceed_to_stripe.html')


@login_required
def payment_success(request, cart_uuid):
	return render(request, 'home/checkout/payment_success.html')


@login_required
def payment_cancel(request):
	return render(request, 'home/checkout/payment_cancel.html')


@login_required
def stripe_test(request):
	# Logged in users only
	if not request.user.is_authenticated:
		return HttpResponseForbidden()
	if request.method == 'POST':
		# Create product
		product = Product.objects.create(
			name="p1",
			description="p1 description",
			price=5,
			estimated_delivery_date=get_random_date(),
			status=Product.ACTIVE,
			stock=5,
			stripe_product_id="will be assigned later",
			stripe_price_id="will be assigned later",
			creator=request.user,
			updater=request.user
		)

		# Create product image
		with open('static/images/pastry1.jpeg', 'rb') as image_file:
			ProductImage.objects.create(
				product=product,
				image=File(image_file),
				creator=request.user,
				updater=request.user
			)

		# Associate that product with stripe product and price objects
		product.create_stripe_product_and_price_objs()

		# Get the cart
		cart = Cart.get_active_cart_or_create_new_cart(request)

		# Create a cart item
		CartItem.objects.create(
			cart=cart,
			product=product,
			quantity=5,
			original_price=product.price,
			creator=request.user,
			updater=request.user
		)

		# Create stripe checkout session
		checkout_url = cart.create_stripe_checkout_session(request)

		# Redirects to stripe checkout URL
		return redirect(checkout_url, code=303)
	else:
		return render(request, 'home/checkout/stripe_test.html')
