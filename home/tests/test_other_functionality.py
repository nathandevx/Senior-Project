from django.test import RequestFactory
from django.template import Context, Template
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
from django.core.files import File
from django.contrib.sites.shortcuts import get_current_site
from senior_project import utils
from home.tests.base import BaseTestCase
from home.models import Product, ProductImage, Cart
from blog.models import Post
import datetime
import requests


class TestUtilityFunctions(BaseTestCase):
	def setUp(self):
		super().setUp()
		self.post = Post.objects.create(title="Post 1", preview_text="Preview text", content="Post content", status=Post.ACTIVE, creator=self.superuser, updater=self.superuser)
		self.factory = RequestFactory()

	def test_format_datetime(self):
		date = timezone.make_aware(datetime.datetime(2023, 1, 1, 6, 30))
		self.assertEqual(utils.format_datetime(date), "January 01, 2023, 06:30 AM")

	def test_get_full_url(self):
		url = '/fake-path/'
		request = self.factory.get(url)
		protocol = 'https' if settings.USE_HTTPS else 'http'
		full_url = f"{protocol}://{get_current_site(request)}{url}"
		self.assertEqual(full_url, utils.get_full_url(url))

	def test_get_allowed_cities(self):
		self.assertEqual(['sacramento'], utils.get_allowed_cities('sacramento'))
		self.assertEqual(['sacramento'], utils.get_allowed_cities('sacramento,'))
		self.assertEqual(['sacramento', 'los angeles'], utils.get_allowed_cities('sacramento, los angeles'))
		self.assertEqual(['sacramento', 'los angeles'], utils.get_allowed_cities('sacramento,los angeles'))


class TestDecorators(BaseTestCase):
	def setUp(self):
		super().setUp()
		self.factory = RequestFactory()

	@staticmethod
	@ utils.superuser_or_admin_required
	def _dummy_superuser_required_view(request):
		return HttpResponse()

	@staticmethod
	@ utils.login_required
	def _dummy_login_required_view(request):
		return HttpResponse()

	def test_superuser_required_with_superuser(self):
		request = self.factory.get('/fake-path/')
		request.user = self.superuser
		response = self._dummy_superuser_required_view(request)
		self.assertEqual(response.status_code, 200)

	def test_superuser_required_with_normal_user(self):
		request = self.factory.get('/fake-path/')
		request.user = self.user1
		response = self._dummy_superuser_required_view(request)
		self.assertEqual(response.status_code, 403)

	def test_superuser_required_with_not_logged_in_user(self):
		request = self.factory.get('/fake-path/')
		request.user = self.anonymous_user
		response = self._dummy_superuser_required_view(request)
		self.assertEqual(response.status_code, 403)

	def test_login_required_with_logged_in_user(self):
		request = self.factory.get('/fake-path/')
		request.user = self.user1
		response = self._dummy_login_required_view(request)
		self.assertEqual(response.status_code, 200)

	def test_login_required_with_not_logged_in_user(self):
		request = self.factory.get('/fake-path/')
		request.user = self.anonymous_user
		response = self._dummy_login_required_view(request)
		self.assertEqual(response.status_code, 403)


class TestTemplateTags(BaseTestCase):
	def setUp(self):
		super().setUp()
		self.factory = RequestFactory()

	def test_cart_tag(self):
		# Create a fake request
		request = self.factory.get('/fake-path/')
		request.user = self.user1

		# Creates a fake template that uses the tag
		template = Template('{% load tags %} {% cart_url %}')

		# Renders the template with the given context.
		rendered_template = template.render(Context({'request': request}))

		# Get the expected cart url
		expected_url = Cart.get_active_cart_or_create_new_cart(request.user).get_read_url()

		# Assert that the template contains the url
		self.assertIn(expected_url, rendered_template)


class TestAWSFunctionality(BaseTestCase):
	def setUp(self):
		super().setUp()
		self._create_objects()
		self.image_url = self.product1_image1.image.url

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
		with open('static/images/for_testing/dummy_image1.jpg', 'rb') as f1:
			image1 = File(f1)
			self.product1_image1 = ProductImage.objects.create(
				product=self.product1,
				image=image1,
				creator=self.superuser,
				updater=self.superuser,
			)

	def test_get_image(self):
		r = requests.get(self.image_url)
		self.assertEqual(200, r.status_code)
		self.assertIn("amazonaws.com", self.image_url)

	def test_get_image_after_product_deletion(self):
		self.product1.delete_images()
		self.product1.delete()
		r = requests.get(self.image_url)
		self.assertEqual(404, r.status_code)
