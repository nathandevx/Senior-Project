from django.shortcuts import reverse
from django.urls import resolve
from home.tests.base import BaseTestCase
from home.models import Product, Cart, CartItem
from home.views import carts


class TestCartCreate(BaseTestCase):
	def setUp(self):
		super().setUp()
		self.client.login(username=self.user1.username, password=self.user1_password)
		# visit the home page, this should create a new cart for the user
		self.client.get('/')

	def test_cart_created_on_signup(self):
		"""When a user first signs up, an active cart is created for them (if they visit any page with the navbar)."""
		cart_count = Cart.objects.filter(creator=self.user1).count()
		first_cart = Cart.objects.filter(creator=self.user1).first()
		self.assertEqual(cart_count, 1)
		self.assertTrue(first_cart.is_active)

	def test_cart_created_on_payment_success(self):
		"""When a user finishes ordering the items in their cart, is a new cart created?"""
		self.client.login(username=self.user1.username, password=self.user1_password)
		cart = Cart.objects.filter(creator=self.user1, status=Cart.ACTIVE).first()
		cart_count = Cart.objects.filter(creator=self.user1).count()
		carts = Cart.objects.filter(creator=self.user1)

		# Visit /payment-success/ to simulate a successful stripe payment
		response = self.client.get(reverse('home:payment-success', kwargs={'cart_uuid': cart.uuid}))

		self.assertEqual(response.status_code, 302)
		self.assertEqual(Cart.objects.filter(creator=self.user1).count(), cart_count+1)
		self.assertTrue(carts[0].is_inactive())
		self.assertTrue(carts[1].is_active())


class TestCartRead(BaseTestCase):
	def setUp(self):
		super().setUp()

	def _create_products(self):
		self.product1 = Product.objects.create(
			name='p1',
			description='description1',
			price=10,
			status=Product.ACTIVE,
			stock=10,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.product2 = Product.objects.create(
			name='p2',
			description='description2',
			price=20,
			status=Product.ACTIVE,
			stock=20,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.product1.create_stripe_product_and_price_objs()
		self.product2.create_stripe_product_and_price_objs()

	def _create_cart_and_cartitems_valid(self, user):
		self._create_products()
		cart = Cart.get_active_cart_or_create_new_cart(user)
		self.cartitem1 = CartItem.objects.create(
			cart=cart,
			product=self.product1,
			original_price=0,
			quantity=2,
			creator=user,
			updater=user,
		)
		self.cartitem2 = CartItem.objects.create(
			cart=cart,
			product=self.product1,
			original_price=0,
			quantity=5,
			creator=user,
			updater=user,
		)
		self.cartitem3 = CartItem.objects.create(
			cart=cart,
			product=self.product2,
			original_price=0,
			quantity=8,
			creator=user,
			updater=user,
		)
		return cart

	def test_user1_access(self):
		"""User1 should be able to access their own cart page"""
		self.client.login(username=self.user1.username, password=self.password)
		cart = Cart.get_active_cart_or_create_new_cart(self.user1)
		response = self.client.get(cart.get_read_url())
		self.assertEqual(response.status_code, 200)

	def test_other_user_access(self):
		"""User2 should not be able to access user1's cart page"""
		self.client.login(username=self.superuser.username, password=self.password)
		cart = Cart.get_active_cart_or_create_new_cart(self.user1)
		response = self.client.get(cart.get_read_url())
		self.assertEqual(response.status_code, 403)

	def test_user1_empty_cart(self):
		self.client.login(username=self.user1.username, password=self.password)
		cart = Cart.get_active_cart_or_create_new_cart(self.user1)
		response = self.client.get(cart.get_read_url())
		context = response.context

		self.assertEqual(resolve(cart.get_read_url()).func, carts.cart_read)
		self.assertTemplateUsed(response, 'home/carts/read.html')
		self.assertEqual(response.status_code, 200)

		self.assertIn('cart', context)
		self.assertIn('formset', context)
		self.assertIn('cart_items_data', context)

		self.assertEqual(context['cart'], cart)
		self.assertEqual(context['cart_items_data'], [])

	def test_user1_non_empty_cart(self):
		self.client.login(username=self.user1.username, password=self.password)
		cart = self._create_cart_and_cartitems_valid(self.user1)

		response = self.client.get(cart.get_read_url())
		context = response.context

		self.assertEqual(resolve(cart.get_read_url()).func, carts.cart_read)
		self.assertTemplateUsed(response, 'home/carts/read.html')
		self.assertEqual(response.status_code, 200)

		self.assertIn('cart', context)
		self.assertIn('formset', context)
		self.assertIn('cart_items_data', context)

		self.assertEqual(context['cart'], cart)
		self.assertEqual(len(context['cart_items_data']), 3)


class TestCartDelete(BaseTestCase):
	def setUp(self):
		super().setUp()
		self.cart = Cart.get_active_cart_or_create_new_cart(self.user1)
		self.url = self.cart.get_delete_url()

	def test_user1_access(self):
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(self.url)
		self.assertEqual(response.status_code, 200)

	def test_other_user_access(self):
		self.client.login(username=self.superuser.username, password=self.password)
		response = self.client.get(self.url)
		self.assertEqual(response.status_code, 403)

	def test_get_request(self):
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(self.url)
		context = response.context

		self.assertEqual(resolve(self.url).func, carts.cart_delete)
		self.assertTemplateUsed(response, 'home/carts/delete.html')
		self.assertEqual(response.status_code, 200)

		self.assertIn('cart', context)

		self.assertEqual(context['cart'], self.cart)

	def test_post_request(self):
		self.client.login(username=self.user1.username, password=self.password)
		initial_count = Cart.objects.count()
		response = self.client.post(self.url)
		self.assertEqual(Cart.objects.count(), initial_count-1)
		self.assertRedirects(response, Product.get_list_url(), status_code=302, target_status_code=200)
