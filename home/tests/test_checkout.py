from django.shortcuts import reverse
from django.urls import resolve
from senior_project import constants
from senior_project.utils import get_allowed_cities
from home.tests.base import BaseTestCase
from home.models import Product, Cart, ShippingAddress
from home.forms import ShippingAddressForm
from home.views import checkout


class CheckoutBaseTestCase(BaseTestCase):
	def setUp(self):
		super().setUp()
		self.product1 = Product.objects.create(
			name='p1',
			description='description1',
			price=5,
			status=Product.ACTIVE,
			stock=10,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.product1.create_stripe_product_and_price_objs()
		self.out_of_stock_product = Product.objects.create(
			name='p11',
			description='description1',
			price=5,
			status=Product.ACTIVE,
			stock=0,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.inactive_product = Product.objects.create(
			name='p111',
			description='description1',
			price=5,
			status=Product.INACTIVE,
			stock=10,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.shipping_address = ShippingAddress.objects.create(
			address='Testing',
			city=get_allowed_cities('sacramento')[0],
			state='Testing',
			country='Testing',
			postal_code=11111,
			creator=self.superuser,
			updater=self.superuser,
		)


class TestShippingAddress(CheckoutBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = reverse("home:shipping-info")

	def test_login_required(self):
		"""Login is required to access the url."""
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 403)

	def test_get_request_cart_errors1(self):
		"""On get request, are users shown the cart_errors.html template if their cart has a product with no stock?"""
		self.client.login(username=self.user1.username, password=self.password)
		cart = Cart.get_active_cart_or_create_new_cart(self.user1)
		self.out_of_stock_product.add_product_to_cart(self.user1, cart, 5)

		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'home/carts/cart_errors.html')

	def test_get_request_cart_errors2(self):
		"""On get request, are users shown the cart_errors.html template if their cart has a product that is inactive?"""
		self.client.login(username=self.user1.username, password=self.password)
		cart = Cart.get_active_cart_or_create_new_cart(self.user1)
		self.inactive_product.add_product_to_cart(self.user1, cart, 5)

		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'home/carts/cart_errors.html')

	def test_get_request_cart_empty(self):
		"""On get request, are users shown the cart_empty.html template if their cart is empty?"""
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'home/carts/cart_empty.html')

	def test_get_request_valid(self):
		"""Tests an error free get request."""
		self.client.login(username=self.user1.username, password=self.password)
		cart = Cart.get_active_cart_or_create_new_cart(self.user1)
		self.product1.add_product_to_cart(self.user1, cart, 5)

		response = self.client.get(self.url)

		self.assertEquals(resolve(self.url).func, checkout.shipping_info)
		self.assertTemplateUsed(response, 'home/checkout/shipping_info.html')
		self.assertEquals(response.status_code, 200)

	def test_post_request_valid(self):
		"""On a valid post request, a user's active cart should now be associated with the valid shipping address."""
		self.client.login(username=self.user1.username, password=self.password)
		cart = Cart.get_active_cart_or_create_new_cart(self.user1)
		self.product1.add_product_to_cart(self.user1, cart, 5)
		form_data = {
			'address': 'address1',
			'city': 'd',
			'state': 'state1',
			'country': 'country1',
			'postal_code': 11111,
		}
		initial_count = ShippingAddress.objects.count()
		response = self.client.post(self.url, data=form_data)

		self.assertEquals(ShippingAddress.objects.count(), initial_count + 1)
		self.assertRedirects(response, reverse("home:proceed-to-stripe"), status_code=302, target_status_code=200)

	def test_post_request_invalid(self):
		"""On a post request, if the user enters a city that is not allowed, the shipping address should not be saved and a validation error should be raised."""
		self.client.login(username=self.user1.username, password=self.password)
		cart = Cart.get_active_cart_or_create_new_cart(self.user1)
		self.product1.add_product_to_cart(self.user1, cart, 5)
		form_data = {
			'address': 'address1',
			'city': 'ddd',  # not a valid city
			'state': 'state1',
			'country': 'country1',
			'postal_code': 11111,
		}
		initial_count = ShippingAddress.objects.count()
		response = self.client.post(self.url, data=form_data)

		self.assertEquals(ShippingAddress.objects.count(), initial_count)
		self.assertFormError(ShippingAddressForm(form_data), 'city', [constants.SHIPPING_ADDRESS_FORM_ERROR])
		self.assertEquals(response.request.get('PATH_INFO'), self.url)
		self.assertEquals(response.status_code, 200)


class TestProceedToStripe(CheckoutBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = reverse("home:proceed-to-stripe")

	def test_login_required(self):
		"""Login is required to access the url."""
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 403)

	def test_get_request_cart_errors1(self):
		"""On get request, are users shown the cart_errors.html template if their cart has a product with no stock?"""
		self.client.login(username=self.user1.username, password=self.password)
		cart = Cart.get_active_cart_or_create_new_cart(self.user1)
		self.out_of_stock_product.add_product_to_cart(self.user1, cart, 5)

		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'home/carts/cart_errors.html')

	def test_get_request_cart_errors2(self):
		"""On get request, are users shown the cart_errors.html template if their cart has a product that is inactive?"""
		self.client.login(username=self.user1.username, password=self.password)
		cart = Cart.get_active_cart_or_create_new_cart(self.user1)
		self.inactive_product.add_product_to_cart(self.user1, cart, 5)

		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'home/carts/cart_errors.html')

	def test_get_request_cart_empty(self):
		"""On get request, are users shown the cart_empty.html template if their cart is empty?"""
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'home/carts/cart_empty.html')

	def test_get_request_no_shipping_address(self):
		"""On a get request, are users shown the no_shipping_info.html template if their cart has no shipping address associate with it?"""
		self.client.login(username=self.user1.username, password=self.password)
		cart = Cart.get_active_cart_or_create_new_cart(self.user1)
		self.product1.add_product_to_cart(self.user1, cart, 5)

		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)
		self.assertTemplateUsed(response, 'home/checkout/no_shipping_info.html')

	def test_get_request_valid(self):
		"""Tests an error free get request."""
		self.client.login(username=self.user1.username, password=self.password)
		cart = Cart.get_active_cart_or_create_new_cart(self.user1)
		self.product1.add_product_to_cart(self.user1, cart, 5)
		cart.set_shipping_address(self.shipping_address)

		response = self.client.get(self.url)

		self.assertEquals(resolve(self.url).func, checkout.proceed_to_stripe)
		self.assertTemplateUsed(response, 'home/checkout/proceed_to_stripe.html')
		self.assertEquals(response.status_code, 200)

	def test_post_request_valid(self):
		"""On a post request, is the user redirected to the stripe checkout session url?"""
		self.client.login(username=self.user1.username, password=self.password)
		cart = Cart.get_active_cart_or_create_new_cart(self.user1)
		self.product1.add_product_to_cart(self.user1, cart, 5)
		cart.set_shipping_address(self.shipping_address)
		checkout_url = cart.create_stripe_checkout_session()
		self.client.post(self.url)
		self.assertIn("https://checkout.stripe.com", checkout_url)


class TestPaymentSuccess(CheckoutBaseTestCase):
	def setUp(self):
		super().setUp()
		self.cart = Cart.get_active_cart_or_create_new_cart(self.user1)
		self.product1.add_product_to_cart(self.user1, self.cart, 5)
		self.cart.set_shipping_address(self.shipping_address)
		self.url = self.cart.get_payment_success_url()

	def test_login_required(self):
		"""Login is required to access the url."""
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 403)

	def test_get_request_valid(self):
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(self.url)
		self.assertEquals(resolve(self.url).func, checkout.payment_success)
		self.assertRedirects(response, self.cart.get_order().get_read_url(), status_code=302, target_status_code=200)

	def test_get_request_invalid(self):
		"""On a get request, if a cart has an order associated with it, /payment-success/ should return a 403."""
		self.client.login(username=self.user1.username, password=self.password)
		self.cart.create_order()
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 403)


class TestPaymentCanceled(CheckoutBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = reverse("home:payment-cancel")

	def test_login_required(self):
		"""Login is required to access the url."""
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 403)

	def test_get_request_no_order_associated_with_cart(self):
		"""On a get request, make sure that there is no order associated with the current active cart."""
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(self.url)
		self.assertFalse(Cart.get_active_cart_or_create_new_cart(self.user1).has_order())
		self.assertEquals(response.status_code, 200)

	def test_get_request_valid(self):
		"""On a get request, is the user shown the correct template?"""
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(self.url)

		self.assertEquals(resolve(self.url).func, checkout.payment_cancel)
		self.assertTemplateUsed(response, 'home/checkout/payment_cancel.html')
		self.assertEquals(response.status_code, 200)
