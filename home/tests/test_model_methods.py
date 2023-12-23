from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.core import mail
from django.core.files import File
from django.shortcuts import reverse
from io import StringIO
from home.tests.base import BaseTestCase
from home.models import Product, ProductImage, ShippingAddress, Cart, CartItem, Order, OrderHistory
from blog.models import Post
from senior_project.exceptions import MoreThanOneActiveCartError, MoreThanOneCartItemError
from senior_project.utils import get_full_url
from senior_project.constants import MONTHS
import csv
import environ
import stripe


env = environ.Env(
	# set casting, default value
	DEBUG=(bool, False)
)

stripe.api_key = env('STRIPE_SECRET_KEY')

User = get_user_model()


class TestProductModelMethods(BaseTestCase):
	def setUp(self):
		super().setUp()
		self._create_objects()

	def _create_objects(self):
		self._create_products()
		self._create_product_images()
		self._create_cart_cartitems_order()

	def _create_products(self):
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
		self.product2 = Product.objects.create(
			name='p2',
			description='description2',
			price=10,
			status=Product.ACTIVE,
			stock=10,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.inactive_product1 = Product.objects.create(
			name='p3',
			description='description3',
			price=10,
			status=Product.INACTIVE,
			stock=10,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.inactive_product2 = Product.objects.create(
			name='p4',
			description='description3',
			price=10,
			status=Product.INACTIVE,
			stock=10,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)

	def _create_product_images(self):
		with open('static/images/for_testing/pastry1.jpeg', 'rb') as f1:
			image1 = File(f1)
			self.product1_image1 = ProductImage.objects.create(
				product=self.product1,
				image=image1,
				creator=self.superuser,
				updater=self.superuser,
			)
		with open('static/images/for_testing/pastry2.jpeg', 'rb') as f2:
			image2 = File(f2)
			self.product1_image2 = ProductImage.objects.create(
				product=self.product1,
				image=image2,
				creator=self.superuser,
				updater=self.superuser,
			)

	def _create_cart_cartitems_order(self):
		self.shipping_address = ShippingAddress.objects.create(
			address='The address',
			city='The city',
			state='The state',
			country='The country',
			postal_code='11111',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.inactive_cart1 = Cart.objects.create(
			status=Cart.INACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.inactive_cart2 = Cart.objects.create(
			status=Cart.INACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.active_cart1 = Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.active_cart2 = Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.active_cart3 = Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem1 = CartItem.objects.create(
			cart=self.inactive_cart1,
			product=self.product1,
			original_price=0,
			quantity=20,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem2 = CartItem.objects.create(
			cart=self.inactive_cart1,
			product=self.product2,
			original_price=0,
			quantity=5,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem3 = CartItem.objects.create(
			cart=self.inactive_cart2,
			product=self.product2,
			original_price=0,
			quantity=5,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem4 = CartItem.objects.create(
			cart=self.active_cart1,
			product=self.product1,
			original_price=0,
			quantity=5,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem5 = CartItem.objects.create(
			cart=self.active_cart2,
			product=self.product2,
			original_price=0,
			quantity=5,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem6 = CartItem.objects.create(
			cart=self.active_cart2,
			product=self.product2,
			original_price=0,
			quantity=5,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.order1 = Order.objects.create(
			cart=self.inactive_cart1,
			total_price=10,
			status=Order.PLACED,
			creator=self.superuser,
			updater=self.superuser,
		)

	def test_get_list_url(self):
		returned_url = Product.get_list_url()
		expected_url = '/'
		self.assertEquals(returned_url, expected_url)

	def test_get_create_url(self):
		returned_url = Product.get_create_url()
		expected_url = '/product/create/'
		self.assertEquals(returned_url, expected_url)

	def test_get_read_url(self):
		returned_url = self.product1.get_read_url()
		expected_url = f'/product/{self.product1.pk}/'
		self.assertEquals(returned_url, expected_url)

	def test_get_update_url(self):
		returned_url = self.product1.get_update_url()
		expected_url = f'/product/update/{self.product1.pk}/'
		self.assertEquals(returned_url, expected_url)

	def test_get_delete_url(self):
		returned_url = self.product1.get_delete_url()
		expected_url = f'/product/delete/{self.product1.pk}/'
		self.assertEquals(returned_url, expected_url)

	def test_is_active(self):
		self.assertTrue(self.product1.is_active())
		self.assertFalse(self.inactive_product1.is_active())

	def test_is_inactive(self):
		self.assertFalse(self.product1.is_inactive())
		self.assertTrue(self.inactive_product1.is_inactive())

	def test_get_images(self):
		self.assertEquals(self.product1.get_images().count(), 2)
		self.assertEquals(self.product1.get_images().first(), self.product1_image1)

	def test_save_and_delete_images(self):
		# Test save_images()
		initial_image_count = self.product2.get_images().count()
		with open('static/images/for_testing/pastry1.jpeg', 'rb') as f1, \
				open('static/images/for_testing/pastry2.jpeg', 'rb') as f2:
			image1 = File(f1)
			image2 = File(f2)
			self.product2.save_images([image1, image2])
		self.assertEquals(self.product2.get_images().count(), initial_image_count + 2)

		# Test delete_images()
		self.product2.delete_images()
		self.assertEquals(self.product2.get_images().count(), 0)

	def test_get_active_products(self):
		self.assertEquals(Product.get_active_products().count(), 2)

	def test_get_top_10_selling_products(self):
		product_names, total_solds = Product.get_top_10_selling_products()
		self.assertEquals(product_names, [self.product1.name, self.product2.name, self.inactive_product1.name, self.inactive_product2.name])
		self.assertEquals(total_solds, [20, 10, 0, 0])

	def test_add_product_to_cart(self):
		with self.assertRaises(MoreThanOneCartItemError):
			self.product2.add_product_to_cart(self.superuser, self.active_cart2, 10)

		initial_count = CartItem.objects.all().count()
		self.product1.add_product_to_cart(self.superuser, self.active_cart3, 10)
		self.assertEquals(CartItem.objects.all().count(), initial_count + 1)

		cartitem = self.product1.add_product_to_cart(self.superuser, self.active_cart1, 10)
		self.assertEquals(cartitem.quantity, 15)

	def test_get_associated_orders(self):
		self.assertEquals(self.product1.get_associated_orders().first(), self.order1)


class TestCartModelMethods(BaseTestCase):
	def setUp(self):
		super().setUp()
		self.factory = RequestFactory()
		self._create_shipping_address()
		self._create_user_with_multiple_active_carts()
		self._create_user_with_no_active_carts()
		self._create_products()
		self._create_carts_and_cartitems_superuser()
		self._create_cart_with_inactive_cartitems()
		self._create_cart_with_out_of_stock_cartitems()

	def _create_products(self):
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
		self.product2 = Product.objects.create(
			name='p2',
			description='description2',
			price=10,
			status=Product.ACTIVE,
			stock=10,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.inactive_product = Product.objects.create(
			name='p3',
			description='description3',
			price=10,
			status=Product.INACTIVE,
			stock=10,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.out_of_stock_product = Product.objects.create(
			name='p4',
			description='description4',
			price=10,
			status=Product.INACTIVE,
			stock=0,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)

	def _create_shipping_address(self):
		self.shipping_address = ShippingAddress.objects.create(
			address='The address',
			city='The city',
			state='The state',
			country='The country',
			postal_code='11111',
			creator=self.superuser,
			updater=self.superuser,
		)

	def _create_user_with_multiple_active_carts(self):
		self.user_with_multiple_active_carts = User.objects.create_user(username='Multiple active carts user', email='example@example.com', password=self.password)
		Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=self.user_with_multiple_active_carts,
			updater=self.user_with_multiple_active_carts,
		)
		Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=self.user_with_multiple_active_carts,
			updater=self.user_with_multiple_active_carts,
		)

	def _create_user_with_no_active_carts(self):
		self.user_with_no_carts = User.objects.create_user(username='No active carts user', email='example@example.com', password=self.password)

	def _create_cart_with_out_of_stock_cartitems(self):
		dummy1 = User.objects.create_user(username='Dummy1', email='example@example.com', password=self.password)
		self.cart_with_out_of_stock_cartitems = Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=dummy1,
			updater=dummy1,
		)
		self.out_of_stock_cartitem = CartItem.objects.create(
			cart=self.cart_with_out_of_stock_cartitems,
			product=self.out_of_stock_product,
			original_price=0,
			quantity=5,
			creator=dummy1,
			updater=dummy1,
		)

	def _create_cart_with_inactive_cartitems(self):
		dummy2 = User.objects.create_user(username='Dummy2', email='example@example.com', password=self.password)
		self.cart_with_inactive_cartitems = Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=dummy2,
			updater=dummy2,
		)
		self.inactive_cartitem = CartItem.objects.create(
			cart=self.cart_with_inactive_cartitems,
			product=self.inactive_product,
			original_price=0,
			quantity=5,
			creator=dummy2,
			updater=dummy2,
		)

	def _create_carts_and_cartitems_superuser(self):
		self.empty_cart = Cart.objects.create(
			status=Cart.INACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.active_cart = Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.inactive_cart = Cart.objects.create(
			status=Cart.INACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem1 = CartItem.objects.create(
			cart=self.active_cart,
			product=self.product1,
			original_price=0,
			quantity=5,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem2 = CartItem.objects.create(
			cart=self.active_cart,
			product=self.product2,
			original_price=0,
			quantity=5,
			creator=self.superuser,
			updater=self.superuser,
		)

	def test_get_read_url(self):
		returned_url = self.active_cart.get_read_url()
		expected_url = f'/cart/{self.active_cart.pk}/'
		self.assertEquals(returned_url, expected_url)

	def test_get_delete_url(self):
		returned_url = self.active_cart.get_delete_url()
		expected_url = f'/cart/delete/{self.active_cart.pk}/'
		self.assertEquals(returned_url, expected_url)

	def test_is_active(self):
		self.assertTrue(self.active_cart.is_active())
		self.assertFalse(self.inactive_cart.is_active())

	def test_is_inactive(self):
		self.assertFalse(self.active_cart.is_inactive())
		self.assertTrue(self.inactive_cart.is_inactive())

	def test_is_empty(self):
		self.assertTrue(self.empty_cart.is_empty())
		self.assertFalse(self.active_cart.is_empty())

	def test_get_total_cart_price(self):
		self.assertEquals(75, self.active_cart.get_total_cart_price())

	def test_get_active_cart_or_create_new_cart(self):
		with self.assertRaises(MoreThanOneActiveCartError):
			Cart.get_active_cart_or_create_new_cart(self.user_with_multiple_active_carts)
		self.assertEquals(self.active_cart, Cart.get_active_cart_or_create_new_cart(self.superuser))
		cart_count = Cart.objects.count()
		Cart.get_active_cart_or_create_new_cart(self.user_with_no_carts)
		self.assertEquals(cart_count + 1, Cart.objects.count())

	def test_set_cart_as_inactive(self):
		with self.assertRaises(MoreThanOneActiveCartError):
			Cart.set_cart_as_inactive(self.user_with_multiple_active_carts)
		with self.assertRaises(ValueError):
			Cart.set_cart_as_inactive(self.user_with_no_carts)
		Cart.set_cart_as_inactive(self.superuser)
		self.assertFalse(Cart.objects.filter(creator=self.superuser, status=Cart.ACTIVE))

	def test_set_original_price_for_all_cart_items(self):
		self.active_cart.set_original_price_for_all_cart_items()
		cartitems = self.active_cart.get_cartitems()
		self.assertTrue(cartitems[0].original_price == 5.00)
		self.assertTrue(cartitems[1].original_price == 10.00)

	def test_has_out_of_stock_or_inactive_products(self):
		stock_limit, inactive_product = self.active_cart.has_out_of_stock_or_inactive_products()
		self.assertFalse(stock_limit)
		self.assertFalse(inactive_product)

		stock_limit, inactive_product = self.cart_with_inactive_cartitems.has_out_of_stock_or_inactive_products()
		self.assertFalse(stock_limit)
		self.assertTrue(inactive_product)

		stock_limit, inactive_product = self.cart_with_out_of_stock_cartitems.has_out_of_stock_or_inactive_products()
		self.assertTrue(stock_limit)
		self.assertTrue(inactive_product)

	def test_get_payment_success_and_payment_cancel_url(self):
		returned_success_url, returned_canceled_url = self.active_cart.get_payment_success_and_payment_cancel_url()
		expected_success_url = get_full_url(f'/checkout/payment-success/{self.active_cart.uuid}/')
		expected_canceled_url = get_full_url('/checkout/payment-cancel/')
		self.assertEquals(returned_success_url, expected_success_url)
		self.assertEquals(returned_canceled_url, expected_canceled_url)

	def test_create_order(self):
		order = self.active_cart.create_order()
		self.assertEquals(order.cart, self.active_cart)
		self.assertEquals(order.status, Order.PLACED)
		self.assertEquals(order.creator, self.active_cart.creator)

	def test_not_creator_or_inactive_cart(self):
		# Test active cart with correct user
		self.assertFalse(self.active_cart.not_creator_or_inactive_cart(self.active_cart.creator))
		# Test active cart with wrong user
		self.assertTrue(self.active_cart.not_creator_or_inactive_cart(self.user1))
		# Test inactive cart with correct user
		self.assertTrue(self.inactive_cart.not_creator_or_inactive_cart(self.inactive_cart.creator))
		# Test inactive cart with wrong user
		self.assertTrue(self.inactive_cart.not_creator_or_inactive_cart(self.user1))


class TestCartItemModelMethods(BaseTestCase):
	def setUp(self):
		super().setUp()
		self._create_objects()

	def _create_objects(self):
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
		self.product2 = Product.objects.create(
			name='p1',
			description='description1',
			price=5,
			status=Product.INACTIVE,
			stock=0,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.shipping_address = ShippingAddress.objects.create(
			address='The address',
			city='The city',
			state='The state',
			country='The country',
			postal_code='11111',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.active_cart = Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.perfect_cartitem = CartItem.objects.create(
			cart=self.active_cart,
			product=self.product1,
			original_price=5,
			quantity=5,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.bad_cartitem = CartItem.objects.create(
			cart=self.active_cart,
			product=self.product2,
			original_price=2,
			quantity=5,
			creator=self.superuser,
			updater=self.superuser,
		)

	def test_perfect_cartitem(self):
		self.assertFalse(self.perfect_cartitem.is_quantity_gt_stock())
		self.assertTrue(self.perfect_cartitem.is_quantity_lte_stock())
		self.assertFalse(self.perfect_cartitem.is_quantity_zero())
		self.assertFalse(self.perfect_cartitem.is_product_inactive())
		self.assertEquals(self.perfect_cartitem.get_total_price(), 25)
		self.assertEquals(self.perfect_cartitem.get_total_original_price(), 25)

	def test_bad_cartitem(self):
		self.assertTrue(self.bad_cartitem.is_quantity_gt_stock())
		self.assertFalse(self.bad_cartitem.is_quantity_lte_stock())
		self.assertFalse(self.bad_cartitem.is_quantity_zero())
		self.assertTrue(self.bad_cartitem.is_product_inactive())
		self.assertEquals(self.bad_cartitem.get_total_price(), 25)
		self.assertEquals(self.bad_cartitem.get_total_original_price(), 10)


class TestOrderModelMethods(BaseTestCase):
	def setUp(self):
		super().setUp()
		self._create_objects()

	def _create_objects(self):
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
		self.product2 = Product.objects.create(
			name='p1',
			description='description1',
			price=5,
			status=Product.ACTIVE,
			stock=20,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.shipping_address = ShippingAddress.objects.create(
			address='The address',
			city='The city',
			state='The state',
			country='The country',
			postal_code='11111',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cart1 = Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cart2 = Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cart3 = Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cart4 = Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cart5 = Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem1 = CartItem.objects.create(
			cart=self.cart1,
			product=self.product1,
			original_price=1,
			quantity=1,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem2 = CartItem.objects.create(
			cart=self.cart2,
			product=self.product2,
			original_price=2,
			quantity=2,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem3 = CartItem.objects.create(
			cart=self.cart2,
			product=self.product2,
			original_price=3,
			quantity=3,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem4 = CartItem.objects.create(
			cart=self.cart3,
			product=self.product2,
			original_price=4,
			quantity=4,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem5 = CartItem.objects.create(
			cart=self.cart4,
			product=self.product1,
			original_price=5,
			quantity=5,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem6 = CartItem.objects.create(
			cart=self.cart5,
			product=self.product1,
			original_price=6,
			quantity=6,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem7 = CartItem.objects.create(
			cart=self.cart1,
			product=self.product2,
			original_price=7,
			quantity=7,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.order1 = Order.objects.create(
			cart=self.cart1,
			total_price=10,
			status=Order.PLACED,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.order2 = Order.objects.create(
			cart=self.cart2,
			total_price=20,
			status=Order.SHIPPED,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.order3 = Order.objects.create(
			cart=self.cart3,
			total_price=30,
			status=Order.DELIVERED,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.order4 = Order.objects.create(
			cart=self.cart4,
			total_price=40,
			status=Order.CANCELED,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.order5 = Order.objects.create(
			cart=self.cart5,
			total_price=50,
			status=Order.CANCELED,
			creator=self.superuser,
			updater=self.superuser,
		)
		# For order1
		self.order_history = OrderHistory.objects.create(
			order_number=1,
			total_price=10,
			status=self.order1.status,
			created_at=self.order1.created_at
		)

	def test_get_list_url(self):
		returned_url = Order.get_list_url()
		expected_url = f'/order/list/'
		self.assertEquals(returned_url, expected_url)

	def test_get_read_url(self):
		returned_url = self.order1.get_read_url()
		expected_url = f'/order-confirmation/{self.order1.uuid}/'
		self.assertEquals(returned_url, expected_url)

	def test_is_placed(self):
		self.assertTrue(self.order1.is_placed())
		self.assertFalse(self.order2.is_placed())

	def test_is_shipped(self):
		self.assertTrue(self.order2.is_shipped())
		self.assertFalse(self.order1.is_shipped())

	def test_is_delivered(self):
		self.assertTrue(self.order3.is_delivered())
		self.assertFalse(self.order1.is_delivered())

	def test_is_canceled(self):
		self.assertTrue(self.order4.is_canceled())
		self.assertFalse(self.order1.is_canceled())

	def test_get_export_data(self):
		response = HttpResponse(content_type='text/tab-separated-values')
		Order.get_export_data(response)

		content = response.content.decode('utf-8')
		reader = list(csv.reader(StringIO(content)))

		# Header
		self.assertEquals(reader[0], ['Order ID\tOrder date\tOrder total price\tOrder status\tUser email\tShipping address\tOrdered products'])

	def test_get_users_orders(self):
		self.assertEquals(Order.get_users_orders(self.superuser).count(), 5)

	def test_send_order_confirmation_email(self):
		with self.assertRaises(Exception):
			self.order1.send_order_confirmation_email()
			self.assertEqual(len(mail.outbox), 1)
			self.assertEqual(mail.outbox[0].subject, 'Order Confirmation')
			self.assertIn(mail.outbox[0].body, '<html><head></head><body><h2>Thanks for your order!</h2><p>Order confirmation page')

	def test_get_year_months_total_orders(self):
		months, months_order_totals = Order.get_year_months_total_orders(self.order1.created_at.year)
		self.assertEquals(months, MONTHS)
		self.assertIn(5, months_order_totals)

	def test_get_years_with_orders(self):
		self.assertEquals(Order.get_years_with_orders().first(), self.order1.created_at.year)

	def test_get_order_statuses(self):
		expected_list = [{'status': 'Canceled', 'total': 2}, {'status': 'Delivered', 'total': 1}, {'status': 'Placed', 'total': 1}, {'status': 'Shipped', 'total': 1}]
		self.assertEquals(list(Order.get_order_statuses()), expected_list)


class TestOrderHistoryModelMethods(BaseTestCase):
	def setUp(self):
		super().setUp()
		self._create_objects()

	def _create_objects(self):
		self.shipping_address = ShippingAddress.objects.create(
			address='The address',
			city='The city',
			state='The state',
			country='The country',
			postal_code='11111',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cart1 = Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cart2 = Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.order1 = Order.objects.create(
			cart=self.cart1,
			total_price=10,
			status=Order.PLACED,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.order2 = Order.objects.create(
			cart=self.cart2,
			total_price=10,
			status=Order.PLACED,
			creator=self.superuser,
			updater=self.superuser,
		)

	def test_create_order_history_objs(self):
		OrderHistory.create_order_history_objs(Order.objects.all())
		self.assertEquals(OrderHistory.objects.count(), 2)


class TestBlogModelMethods(BaseTestCase):
	def setUp(self):
		super().setUp()
		self._create_objects()

	def _create_objects(self):
		self.post1 = Post.objects.create(
			title='blog1',
			preview_text='text1',
			status=Post.ACTIVE,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.post2 = Post.objects.create(
			title='blog2',
			preview_text='text2',
			status=Post.ACTIVE,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.inactive_post1 = Post.objects.create(
			title='blog2',
			preview_text='text2',
			status=Post.INACTIVE,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.inactive_post2 = Post.objects.create(
			title='blog2',
			preview_text='text2',
			status=Post.INACTIVE,
			creator=self.superuser,
			updater=self.superuser,
		)

	def test_get_list_url(self):
		returned_url = Post.get_list_url()
		expected_url = f'/blog/posts/'
		self.assertEquals(returned_url, expected_url)

	def test_get_create_url(self):
		returned_url = Post.get_create_url()
		expected_url = f'/blog/post/create/'
		self.assertEquals(returned_url, expected_url)

	def test_get_read_url(self):
		returned_url = self.post1.get_read_url()
		expected_url = f'/blog/post/{self.post1.pk}/'
		self.assertEquals(returned_url, expected_url)

	def test_get_update_url(self):
		returned_url = self.post1.get_update_url()
		expected_url = f'/blog/post/update/{self.post1.pk}/'
		self.assertEquals(returned_url, expected_url)

	def test_get_delete_url(self):
		returned_url = self.post1.get_delete_url()
		expected_url = f'/blog/post/delete/{self.post1.pk}/'
		self.assertEquals(returned_url, expected_url)

	def test_get_active_posts(self):
		self.assertEquals(Post.get_active_posts().count(), 2)

	def test_is_superuser_or_active_post(self):
		self.assertTrue(self.post1.is_superuser_or_active_post(self.superuser))
		self.assertTrue(self.inactive_post1.is_superuser_or_active_post(self.superuser))

		self.assertTrue(self.post1.is_superuser_or_active_post(self.user1))
		self.assertFalse(self.inactive_post1.is_superuser_or_active_post(self.user1))


# Stripe related model methods
class TestCheckoutModelMethods(BaseTestCase):
	def setUp(self):
		super().setUp()
		self.factory = RequestFactory()
		self._create_objects()

	def _create_objects(self):
		self.shipping_address = ShippingAddress.objects.create(
			address='The address',
			city='The city',
			state='The state',
			country='The country',
			postal_code='11111',
			creator=self.superuser,
			updater=self.superuser,
		)
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
		self.product2 = Product.objects.create(
			name='p2',
			description='description2',
			price=10,
			status=Product.ACTIVE,
			stock=10,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.product1.create_stripe_product_and_price_objs()
		self.product2.create_stripe_product_and_price_objs()
		self.cart = Cart.objects.create(
			status=Cart.ACTIVE,
			shipping_address=self.shipping_address,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem1 = CartItem.objects.create(
			cart=self.cart,
			product=self.product1,
			original_price=0,
			quantity=5,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem2 = CartItem.objects.create(
			cart=self.cart,
			product=self.product1,
			original_price=0,
			quantity=5,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.cartitem3 = CartItem.objects.create(
			cart=self.cart,
			product=self.product2,
			original_price=0,
			quantity=8,
			creator=self.superuser,
			updater=self.superuser,
		)

	def test_create_stripe_product_and_price_objs(self):
		# Create stripe product and price objects
		self.product1.create_stripe_product_and_price_objs()
		self.product2.create_stripe_product_and_price_objs()

		# Check if stripe product ID was assigned
		self.assertNotEquals(self.product1.stripe_product_id, '')
		self.assertNotEquals(self.product2.stripe_product_id, '')

		# Check if stripe price ID was assigned
		self.assertNotEquals(self.product1.stripe_price_id, '')
		self.assertNotEquals(self.product2.stripe_price_id, '')

		# Attempt to retrieve stripe product
		p1 = stripe.Product.retrieve(self.product1.stripe_product_id)
		p2 = stripe.Product.retrieve(self.product2.stripe_product_id)

		# Check if name was assigned correctly
		self.assertEquals(p1.name, self.product1.name)
		self.assertEquals(p2.name, self.product2.name)

		# Attempt to retrieve stripe price
		price1 = stripe.Price.retrieve(self.product1.stripe_price_id)
		price2 = stripe.Price.retrieve(self.product2.stripe_price_id)

		# Check if the price was assigned correctly
		self.assertEquals(price1.unit_amount/100, self.product1.price)
		self.assertEquals(price2.unit_amount/100, self.product2.price)

	def test_update_stripe_product_and_price_objs(self):
		# Change the product name and price
		self.product1.name = 'p11'
		self.product2.name = 'p22'
		self.product1.price = 100
		self.product2.price = 200

		self.product1.update_stripe_product_and_price_objs()
		self.product2.update_stripe_product_and_price_objs()

		# Attempt to retrieve stripe product
		p1 = stripe.Product.retrieve(self.product1.stripe_product_id)
		p2 = stripe.Product.retrieve(self.product2.stripe_product_id)

		# Check if name was assigned correctly
		self.assertEquals(self.product1.name, p1.name)
		self.assertEquals(self.product2.name, p2.name)

		# Attempt to retrieve stripe price
		price1 = stripe.Price.retrieve(self.product1.stripe_price_id)
		price2 = stripe.Price.retrieve(self.product2.stripe_price_id)

		# Check if the price was assigned correctly
		self.assertEquals(price1.unit_amount / 100, 100)
		self.assertEquals(price2.unit_amount / 100, 200)

	def test_create_stripe_checkout_session(self):
		self.cart.create_stripe_checkout_session()
		sessions = stripe.checkout.Session.list(limit=1)
		actual_url = sessions.data[0].success_url
		expected_url = get_full_url(reverse('home:payment-success', kwargs={'cart_uuid': self.cart.uuid}))
		self.assertEquals(actual_url, expected_url)

	def test_handle_cart_purchase(self):
		request = self.factory.get('/fake-path/')
		order = self.cart.create_order()
		self.cart.handle_cart_purchase(request, order)
		# Product 1: price=5, stock=10
		# Product 2: price=10, stock=10
		# CartItem 1: quantity=5, product=p1
		# CartItem 2: quantity=5, product=p1
		# CartItem 3: quantity=8, product=p2
		# Product 1: total=50, stock=0
		# Product 2: total=80, stock=2
		# Total = 130
		products = Product.objects.all()
		self.assertEquals(products[0].stock, 0)
		self.assertEquals(products[1].stock, 2)
		self.assertEquals(order.total_price, 130)

	def test_delete_product_and_set_stripe_product_as_inactive(self):
		initial_count = Product.objects.all().count()
		stripe_product_id = self.product1.stripe_product_id
		self.product1.delete_product_and_set_stripe_product_as_inactive()

		stripe_product_id_status = stripe.Product.retrieve(stripe_product_id)
		self.assertEquals(Product.objects.all().count(), initial_count-1)
		self.assertFalse(stripe_product_id_status.active)
