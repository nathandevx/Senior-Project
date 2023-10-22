from django.test import RequestFactory
from django.template import Context, Template
from django.utils import timezone
from django.http import HttpResponse
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from home.tests.base import BaseTestCase
from home.models import Cart, Configurations
from blog.models import Post
from senior_project import utils
import datetime


class TestUtilityFunctions(BaseTestCase):
	def setUp(self):
		super().setUp()
		self.post = Post.objects.create(title="Post 1", preview_text="Preview text", content="Post content", status=Post.ACTIVE, creator=self.superuser, updater=self.superuser)
		self.factory = RequestFactory()

	def test_format_datetime(self):
		date = timezone.make_aware(datetime.datetime(2023, 1, 1, 6, 30))
		self.assertEquals(utils.format_datetime(date), "January 01, 2023, 06:30 AM")

	def test_get_full_url(self):
		url = '/fake-path/'
		request = self.factory.get(url)
		protocol = 'https' if settings.USE_HTTPS else 'http'
		full_url = f"{protocol}://{get_current_site(request)}{url}"
		self.assertEquals(full_url, utils.get_full_url(url, request))

	def test_get_random_date(self):
		"""No tests needed, only used in development."""
		pass

	def test_get_allowed_cities(self):
		self.assertEquals(['sacramento'], utils.get_allowed_cities('sacramento'))
		self.assertEquals(['sacramento'], utils.get_allowed_cities('sacramento,'))
		self.assertEquals(['sacramento', 'los angeles'], utils.get_allowed_cities('sacramento, los angeles'))
		self.assertEquals(['sacramento', 'los angeles'], utils.get_allowed_cities('sacramento,los angeles'))

	def test_combine_form_dicts(self):
		"""No tests needed, uses built-in Python code."""
		pass


class TestDecorators(BaseTestCase):
	def setUp(self):
		super().setUp()
		self.factory = RequestFactory()

	@staticmethod
	@ utils.superuser_required
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
		self.assertEquals(response.status_code, 200)

	def test_superuser_required_with_normal_user(self):
		request = self.factory.get('/fake-path/')
		request.user = self.user1
		response = self._dummy_superuser_required_view(request)
		self.assertEquals(response.status_code, 403)

	def test_superuser_required_with_not_logged_in_user(self):
		request = self.factory.get('/fake-path/')
		request.user = self.anonymous_user
		response = self._dummy_superuser_required_view(request)
		self.assertEquals(response.status_code, 403)

	def test_login_required_with_logged_in_user(self):
		request = self.factory.get('/fake-path/')
		request.user = self.user1
		response = self._dummy_login_required_view(request)
		self.assertEquals(response.status_code, 200)

	def test_login_required_with_not_logged_in_user(self):
		request = self.factory.get('/fake-path/')
		request.user = self.anonymous_user
		response = self._dummy_login_required_view(request)
		self.assertEquals(response.status_code, 403)


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
		expected_url = Cart.get_active_cart_or_create_new_cart(request).get_read_url()

		# Assert that the template contains the url
		self.assertIn(expected_url, rendered_template)

	def test_configuration_tag(self):
		# Create a fake request
		request = self.factory.get('/fake-path/')
		request.user = self.user1

		# Creates a fake template that uses the tag
		template = Template('{% load tags %} {% config_url %}')

		# Renders the template with the given context.
		rendered_template = template.render(Context({'request': request}))

		# Check if the url is right
		if Configurations.config_exists():
			url = Configurations.get_first_configuration().get_read_url()
			self.assertIn(url, rendered_template)
		else:
			url = Configurations.get_create_url()
			self.assertIn(url, rendered_template)
