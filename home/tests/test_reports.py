from django.shortcuts import reverse
from django.test import RequestFactory
from django.urls import resolve
from senior_project.utils import get_table_data
from home.tests.base import BaseTestCase
from home.models import Product, Cart, Order
from home.views import reports
from blog.models import Post
from html.parser import HTMLParser
from datetime import datetime
import warnings

warnings.filterwarnings(
	"ignore",
	"DateTimeField .* received a naive datetime .* while time zone support is active.",
	RuntimeWarning
)


class ReportBaseTestCase(BaseTestCase):
	def setUp(self):
		super().setUp()
		self.factory = RequestFactory()

	def _superuser_access(self, url):
		self.client.login(username=self.superuser.username, password=self.password)
		response = self.client.get(url)
		return response.status_code

	def _non_superuser_access(self, url):
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(url)
		return response.status_code

	def _test_access(self, url):
		superuser = self._superuser_access(url)
		non_superuser = self._non_superuser_access(url)
		self.assertEqual(superuser, 200)
		self.assertEqual(non_superuser, 403)

	def _create_orders(self, count: int = 1):
		orders = {}
		fixed_time = datetime(2023, 12, 8, 12, 12, 12, 12000)
		for i in range(0, count):
			cart = Cart.objects.create(
				status=Cart.INACTIVE,
				creator=self.superuser,
				updater=self.superuser
			)
			order = Order.objects.create(
				cart=cart,
				total_price=10,
				status=Order.PLACED if i % 2 == 0 else Order.CANCELED,
				creator=self.superuser,
				updater=self.superuser,
			)
			order.created_at = fixed_time
			order.updated_at = fixed_time
			order.save()
			orders[f'order{i + 1}'] = order
		return orders

class TestReportList(ReportBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = reverse('home:report-list')

	def test_access(self):
		self._test_access(self.url)

	def test_view(self):
		"""Are the expected urls rendered (report orders, report charts, etc). """
		self._superuser_login()
		r = self.client.get(self.url)
		content = r.content.decode()
		orders_link = f"""<p><a href="{reverse('home:report-orders')}">Orders Table</a></p>"""
		api_status_link = f"""<p><a href="{reverse('home:report-api-status')}">API Status</a></p>"""

		self.assertIn(orders_link, content)
		self.assertIn(api_status_link, content)
		self.assertEqual(resolve(self.url).func, reports.report_list)
		self.assertTemplateUsed(r, 'home/reports/list.html')
		self.assertEqual(r.status_code, 200)


class TestReportOrders(ReportBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = reverse('home:report-orders')

	def test_access(self):
		self._test_access(self.url)

	def test_view_no_filters(self):
		self._superuser_login()
		r = self.client.get(self.url)
		content = r.content.decode()
		no_orders = f"""You have no orders."""

		self.assertIn(no_orders, content)
		self.assertEqual(resolve(self.url).func, reports.report_orders)
		self.assertTemplateUsed(r, 'home/reports/orders.html')
		self.assertEqual(r.status_code, 200)

	def test_view_with_filters(self):
		self.client.login(username=self.superuser.username, password=self.password)
		self._create_orders(3)
		request = self.factory.get('/dummy-url/', {"status": Order.PLACED, "order_by": "asc"})
		orders, order_by = get_table_data(request, Order)

		self.assertEqual(len(orders), 2)
		self.assertEqual(order_by, 'asc')

		for order in orders:
			self.assertEqual(order.status, Order.PLACED)


class TestReportProducts(ReportBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = reverse('home:report-products')

	def _create_products(self, count: int = 1):
		products = {}
		for i in range(0, count):
			product = Product.objects.create(
				name=f'p{i+1}',
				description='description',
				price=5,
				status=Product.ACTIVE if i % 2 == 0 else Product.INACTIVE,
				stock=5,
				stripe_product_id='...',
				stripe_price_id='...',
				creator=self.superuser,
				updater=self.superuser,
			)
			products[f'product{i + 1}'] = product
		return products

	def test_access(self):
		self._test_access(self.url)

	def test_view_no_filters(self):
		self._superuser_login()
		r = self.client.get(self.url)
		content = r.content.decode()
		no_products = f"""You have no products."""

		self.assertIn(no_products, content)
		self.assertEqual(resolve(self.url).func, reports.report_products)
		self.assertTemplateUsed(r, 'home/reports/products.html')
		self.assertEqual(r.status_code, 200)

	def test_view_with_filters(self):
		self.client.login(username=self.superuser.username, password=self.password)
		self._create_products(3)
		request = self.factory.get('/dummy-url/', {"status": Product.ACTIVE, "order_by": "asc"})
		products, order_by = get_table_data(request, Product)

		self.assertEqual(len(products), 2)
		self.assertEqual(order_by, 'asc')
		self.assertEqual(products[0].name, 'p1')
		self.assertEqual(products[1].name, 'p3')

		for product in products:
			self.assertEqual(product.status, Product.ACTIVE)


class TestReportBlogs(ReportBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = reverse('home:report-blogs')

	def _create_posts(self, count: int = 1):
		posts = {}
		for i in range(0, count):
			post = Post.objects.create(
				title=f"p{i+1}",
				preview_text="Preview text",
				content="Post content",
				status=Post.ACTIVE if i % 2 == 0 else Post.INACTIVE,
				creator=self.superuser,
				updater=self.superuser),
			posts[f'post{i + 1}'] = post
		return posts

	def test_access(self):
		self._test_access(self.url)

	def test_view_no_filters(self):
		self._superuser_login()
		r = self.client.get(self.url)
		content = r.content.decode()
		no_posts = f"""You have no blog posts."""

		self.assertIn(no_posts, content)
		self.assertEqual(resolve(self.url).func, reports.report_blogs)
		self.assertTemplateUsed(r, 'home/reports/blogs.html')
		self.assertEqual(r.status_code, 200)

	def test_view_with_filters(self):
		self.client.login(username=self.superuser.username, password=self.password)
		self._create_posts(3)
		request = self.factory.get('/dummy-url/', {"status": Post.ACTIVE, "order_by": "asc"})
		posts, order_by = get_table_data(request, Post)

		self.assertEqual(len(posts), 2)
		self.assertEqual(order_by, 'asc')
		self.assertEqual(posts[0].title, 'p1')
		self.assertEqual(posts[1].title, 'p3')

		for post in posts:
			self.assertEqual(post.status, Post.ACTIVE)


class TestReportCharts(ReportBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url1 = reverse('home:report-charts')

	def test_access(self):
		self._test_access(self.url1)


class TestReportExport(ReportBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = reverse('home:report-export')

	def test_access(self):
		self._test_access(self.url)

	def test_view(self):
		self._superuser_login()
		r = self.client.get(self.url)
		content = r.content.decode()
		button = """<button type="submit" class="btn btn-primary">Download</button>"""
		action_link = f"""action="{reverse('home:report-export-download')}" """

		self.assertIn(button, content)
		self.assertIn(action_link, content)
		self.assertEqual(resolve(self.url).func, reports.report_export)
		self.assertTemplateUsed(r, 'home/reports/export.html')
		self.assertEqual(r.status_code, 200)


class TestReportExportDownload(ReportBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = reverse('home:report-export-download')

	def test_access(self):
		self._test_access(self.url)

	def test_empty_export(self):
		self._superuser_login()
		r = self.client.get(self.url)
		content = r.content.decode()
		header = """Order ID\tOrder date\tOrder total price\tOrder status\tUser email\tShipping address\tOrdered products\r\n"""
		self.assertIn(header, content)
		self.assertEqual(r['Content-Type'], 'text/tsv')
		self.assertIn('attachment; filename="report.tsv"', r['Content-Disposition'])
		self.assertEqual(resolve(self.url).func, reports.report_export_download)
		self.assertEqual(r.status_code, 200)

	def test_non_empty_export(self):
		self._superuser_login()
		self._create_orders(2)
		r = self.client.get(self.url)
		content = r.content.decode()
		find = f"""Order ID\tOrder date\tOrder total price\tOrder status\tUser email\tShipping address\tOrdered products\r\n1\t2023-12-08 20:12:12.012000+00:00\t10.00\tPlaced\t{self.superuser.email}\t\t[]\r\n2\t2023-12-08 20:12:12.012000+00:00\t10.00\tCanceled\t{self.superuser.email}\t\t[]\r\n"""

		self.assertIn(find, content)
		self.assertEqual(r['Content-Type'], 'text/tsv')
		self.assertIn('attachment; filename="report.tsv"', r['Content-Disposition'])
		self.assertEqual(resolve(self.url).func, reports.report_export_download)
		self.assertEqual(r.status_code, 200)


class TestReportAPIStatus(ReportBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = reverse('home:report-api-status')
		self.parser = HTMLParser()

	def test_access(self):
		self._test_access(self.url)

	def test_view(self):
		self._superuser_login()
		r = self.client.get(self.url)
		content = r.content.decode()

		self.assertEqual(content.count("Working"), 3)
		self.assertEqual(resolve(self.url).func, reports.report_api_status)
		self.assertTemplateUsed(r, 'home/reports/api_status.html')
		self.assertEqual(r.status_code, 200)


class TestTableDataUtilFunction(BaseTestCase):
	def setUp(self):
		super().setUp()
		self.factory = RequestFactory()

	def _create_products(self, count: int = 1):
		products = {}
		for i in range(0, count):
			product = Product.objects.create(
				name=f'p{i+1}',
				description='description',
				price=10 * i+1,
				status=Product.ACTIVE if i % 2 == 0 else Product.INACTIVE,
				stock=10 * i+1,
				stripe_product_id='...',
				stripe_price_id='...',
				creator=self.superuser,
				updater=self.superuser,
			)
			products[f'product{i+1}'] = product, product.pk
		return products

	def test_no_filters(self):
		self.client.login(username=self.superuser.username, password=self.password)
		self._create_products(2)
		request = self.factory.get('/dummy-url/')
		products, order_by = get_table_data(request, Product)

		self.assertEqual(len(products), 2)
		self.assertEqual(order_by, 'desc')  # Default order_by

	def test_with_filters(self):
		self.client.login(username=self.superuser.username, password=self.password)
		self._create_products(3)
		request = self.factory.get('/dummy-url/', {"status": Product.ACTIVE, "order_by": "asc"})
		products, order_by = get_table_data(request, Product)

		self.assertEqual(len(products), 2)
		self.assertEqual(products[0].name, "p1")
		self.assertEqual(products[1].name, "p3")
		self.assertEqual(order_by, 'asc')
