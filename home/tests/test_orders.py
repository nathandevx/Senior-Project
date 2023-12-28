from django.urls import resolve
from senior_project import constants
from home.tests.base import BaseTestCase
from home.models import Cart, Order
from home.views import orders
from home.forms import OrderForm
import datetime


class OrderBaseTestCase(BaseTestCase):
	def setUp(self):
		super().setUp()
		self._create_objects()

	def _create_objects(self):
		self.cart1 = Cart.objects.create(
			status=Cart.INACTIVE,
			creator=self.user1,
			updater=self.user1,
		)
		self.cart2 = Cart.objects.create(
			status=Cart.INACTIVE,
			creator=self.user1,
			updater=self.user1,
		)
		self.cart3 = Cart.objects.create(
			status=Cart.INACTIVE,
			creator=self.superuser,
			updater=self.superuser,
		)
		self.order1 = Order.objects.create(
			cart=self.cart1,
			total_price=10,
			status=Order.PLACED,
			creator=self.user1,
			updater=self.user1,
		)
		self.order2 = Order.objects.create(
			cart=self.cart2,
			total_price=20,
			status=Order.PLACED,
			creator=self.user1,
			updater=self.user1,
		)
		self.order3 = Order.objects.create(
			cart=self.cart3,
			total_price=30,
			status=Order.PLACED,
			creator=self.superuser,
			updater=self.superuser,
		)


class TestOrdersList(OrderBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = Order.get_list_url()

	def test_login_required(self):
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 403)

	def test_user_access(self):
		"""Make sure they can access their order list page and that they are only shown their orders."""
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(self.url)
		context = response.context

		self.assertEquals(resolve(self.url).func, orders.order_list)
		self.assertTemplateUsed(response, 'home/orders/list.html')
		self.assertEquals(response.status_code, 200)

		self.assertIn('orders', context)

		self.assertEqual(len(context['orders']), 2)

		for order in context['orders']:
			self.assertEquals(order.creator, self.user1)


class TestOrderConfirmation(OrderBaseTestCase):
	def setUp(self):
		super().setUp()
		self.user_1_url = self.order1.get_read_url()

	def test_login_required(self):
		response = self.client.get(self.user_1_url)
		self.assertEquals(response.status_code, 403)

	def test_incorrect_user_access(self):
		"""Superusers can access other users order confirmation pages but normal users can't"""
		self.client.login(username=self.user2.username, password=self.password)
		response = self.client.get(self.user_1_url)
		self.assertEquals(response.status_code, 403)

	def test_superuser_access(self):
		"""The superuser should be able to access a user's order confirmation page."""
		self.client.login(username=self.superuser.username, password=self.password)
		response = self.client.get(self.user_1_url)
		self.assertEquals(response.status_code, 200)

	def test_get_request(self):
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(self.user_1_url)
		context = response.context

		self.assertEquals(resolve(self.user_1_url).func, orders.order_confirmation)
		self.assertTemplateUsed(response, 'home/orders/read.html')
		self.assertEquals(response.status_code, 200)

		self.assertIn('order', context)
		self.assertIn('order_model', context)
		self.assertIn('form', context)

		self.assertEquals(context['order'], self.order1)
		self.assertEquals(context['order_model'], Order)
		self.assertIsInstance(context['form'], OrderForm)

	def test_post_request_valid(self):
		"""A superuser can submit a form on a user's order confirmation page."""
		self.client.login(username=self.superuser.username, password=self.password)
		form_data = {
			'status': Order.DELIVERED,
			'estimated_delivery_date': datetime.date(2023, 12, 8),
			'notes': 'MY NOTES!',
		}
		previous_notes = self.order1.notes
		response = self.client.post(self.user_1_url, data=form_data)
		order = Order.objects.get(pk=self.order1.pk)
		self.assertEquals(order.notes, 'MY NOTES!')
		self.assertNotEquals(previous_notes, order.notes)
		self.assertRedirects(response, self.user_1_url, status_code=302, target_status_code=200)

	def test_post_request_invalid(self):
		"""If Order.CANCELED then the estimated_delivery_date must be none."""
		self.client.login(username=self.superuser.username, password=self.password)
		form_data = {
			'status': Order.CANCELED,
			'estimated_delivery_date': datetime.date(2023, 12, 8),
			'notes': 'MY NOTES!',
		}
		response = self.client.post(self.user_1_url, data=form_data)
		order = Order.objects.get(pk=self.order1.pk)
		self.assertEquals(order.notes, '')
		self.assertNotEquals(order.notes, 'MY NOTES!')
		self.assertFormError(OrderForm(form_data), 'estimated_delivery_date', [constants.ORDER_FORM_ERROR])
		self.assertEquals(response.request.get('PATH_INFO'), self.user_1_url)
		self.assertEquals(response.status_code, 200)