from django.urls import resolve
from django.shortcuts import reverse
from senior_project import constants
from home.tests.base import BaseTestCase
from home.models import Configurations
from home.views import configuration
from home.forms import ConfigurationForm


class ConfigBaseTestCase(BaseTestCase):
	def setUp(self):
		super().setUp()

	@staticmethod
	def _create_config():
		obj = Configurations.objects.create(
			phone_number='123-456-7890',
			email='example@example.com',
			address='1234 Address avenue',
			facebook_url='https://facebook.com',
			instagram_url='https://instagram.com',
		)
		return obj

	def _superuser_access(self, url):
		self.client.login(username=self.superuser.username, password=self.password)
		response = self.client.get(url)
		return response.status_code

	def _non_superuser_access(self, url):
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(url)
		return response.status_code

	def _superuser_login(self):
		self.client.login(username=self.superuser.username, password=self.superuser_password)


class TestConfigCreate(ConfigBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = Configurations.get_create_url()

	def test_access(self):
		superuser = self._superuser_access(self.url)
		non_superuser = self._non_superuser_access(self.url)
		self.assertEquals(superuser, 200)
		self.assertEquals(non_superuser, 403)

	def test_get_request_no_config(self):
		"""On a get request, if there is no config, a form should be displayed"""
		self._superuser_login()
		r = self.client.get(self.url)

		self.assertEquals(resolve(self.url).func, configuration.config_create)
		self.assertTemplateUsed(r, 'home/config/create.html')
		self.assertEquals(r.status_code, 200)
		self.assertIn('form', r.context)
		self.assertIsInstance(r.context['form'], ConfigurationForm)

	def test_get_request_with_config(self):
		"""On a get request, if there is a config, they should be redirected to the config read page."""
		self._superuser_login()
		config = self._create_config()
		r = self.client.get(self.url)

		self.assertRedirects(r, config.get_read_url(), status_code=302, target_status_code=200)

	def test_post_request_with_config(self):
		"""Similar to test_get_request_with_config."""
		self._superuser_login()
		config = self._create_config()
		r = self.client.post(self.url)

		self.assertRedirects(r, config.get_read_url(), status_code=302, target_status_code=200)

	def test_valid_post_request_with_no_config(self):
		"""On a post request, if there is no config and the form is valid, they should be redirected to config read page."""
		self._superuser_login()
		form_data = {
			'phone_number': '123',
			'email': 'example@example.com',
			'address': '123',
			'facebook_url': 'https://facebook.com',
			'instagram_url': 'https://instagram.com',
		}
		r = self.client.post(self.url, data=form_data)
		new_config = Configurations.get_first_configuration()

		self.assertEquals(Configurations.objects.count(), 1)
		self.assertRedirects(r, new_config.get_read_url(), status_code=302, target_status_code=200)

	def test_invalid_post_request_with_no_config(self):
		"""Similar to test_valid_post_request_with_no_config, except since the form is invalid, they remain on the create page."""
		self._superuser_login()
		form_data = {
			'phone_number': '123',
			'email': 'exampleexample.com',  # invalid email
			'address': '123',
			'facebook_url': 'https://facebook.com',
			'instagram_url': 'https://instagram.com',
		}
		r = self.client.post(self.url, data=form_data)

		self.assertEquals(Configurations.objects.count(), 0)
		self.assertFormError(ConfigurationForm(data=form_data), 'email', [constants.EMAIL_FORM_ERROR])
		self.assertEquals(r.request.get('PATH_INFO'), self.url)
		self.assertEquals(r.status_code, 200)


class TestConfigRead(ConfigBaseTestCase):
	def test_access(self):
		url = self._create_config().get_read_url()
		superuser = self._superuser_access(url)
		non_superuser = self._non_superuser_access(url)
		self.assertEquals(superuser, 200)
		self.assertEquals(non_superuser, 403)

	def test_request_no_config(self):
		"""If there is no config, they are redirected to create a config."""
		self._superuser_login()
		r = self.client.get(reverse('home:config-read', kwargs={'pk': 1}))
		self.assertRedirects(r, Configurations.get_create_url(), status_code=302, target_status_code=200)

	def test_request_with_config(self):
		"""If there is a config, they should be shown the read page."""
		self._superuser_login()
		config = self._create_config()
		url = config.get_read_url()
		r = self.client.get(url)

		self.assertEquals(resolve(url).func, configuration.config_read)
		self.assertTemplateUsed(r, 'home/config/read.html')
		self.assertEquals(r.status_code, 200)
		self.assertIn('config', r.context)
		self.assertEquals(r.context['config'], config)


class TestConfigUpdate(ConfigBaseTestCase):
	def setUp(self):
		super().setUp()

	def test_access(self):
		url = self._create_config().get_update_url()
		superuser = self._superuser_access(url)
		non_superuser = self._non_superuser_access(url)
		self.assertEquals(superuser, 200)
		self.assertEquals(non_superuser, 403)

	def test_get_request_no_config(self):
		"""On a get request, if there is no config, they should be redirected to create a config."""
		self._superuser_login()
		r = self.client.get(reverse('home:config-update', kwargs={'pk': 1}))
		self.assertRedirects(r, Configurations.get_create_url(), status_code=302, target_status_code=200)

	def test_get_request_with_config(self):
		"""On a get request, if there is a config, they should be shown a form to update the config."""
		self._superuser_login()
		config = self._create_config()
		url = config.get_update_url()
		r = self.client.get(url)

		self.assertEquals(resolve(url).func, configuration.config_update)
		self.assertTemplateUsed(r, 'home/config/update.html')
		self.assertEquals(r.status_code, 200)
		self.assertIn('config', r.context)
		self.assertIn('form', r.context)
		self.assertEquals(r.context['config'], config)
		self.assertIsInstance(r.context['form'], ConfigurationForm)

	def test_post_request_no_config(self):
		"""Similar to test_get_request_no_config."""
		self._superuser_login()
		r = self.client.post(reverse('home:config-update', kwargs={'pk': 1}))
		self.assertRedirects(r, Configurations.get_create_url(), status_code=302, target_status_code=200)

	def test_valid_post_request_with_config(self):
		"""On a post request, if there is a config and the form is valid, they should be redirected to config read page."""
		self._superuser_login()
		config = self._create_config()
		form_data = {
			'phone_number': '123',
			'email': 'example@example.com',
			'address': '123',
			'facebook_url': 'https://facebook.com',
			'instagram_url': 'https://instagram.com',
		}
		r = self.client.post(config.get_update_url(), data=form_data)
		self.assertEquals(Configurations.objects.count(), 1)
		self.assertRedirects(r, config.get_read_url(), status_code=302, target_status_code=200)

	def test_invalid_post_request_with_config(self):
		"""Similar to test_valid_post_request_with_config, except since the form is invalid, they remain on the update page."""
		self._superuser_login()
		config = self._create_config()
		url = config.get_update_url()
		form_data = {
			'phone_number': '123',
			'email': 'exampleexample.com',  # invalid email
			'address': '123',
			'facebook_url': 'https://facebook.com',
			'instagram_url': 'https://instagram.com',
		}
		r = self.client.post(url, data=form_data)

		self.assertEquals(Configurations.objects.count(), 1)
		self.assertEquals(Configurations.get_first_configuration().phone_number, '123-456-7890')  # make sure the field didn' change
		self.assertFormError(ConfigurationForm(data=form_data), 'email', [constants.EMAIL_FORM_ERROR])
		self.assertEquals(r.request.get('PATH_INFO'), url)
		self.assertEquals(r.status_code, 200)