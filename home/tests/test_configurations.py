from home.tests.base import BaseTestCase
from home.models import Configurations


class ConfigBaseTestCase(BaseTestCase):
	def setUp(self):
		super().setUp()

	@staticmethod
	def _create_config():
		config = Configurations.objects.create(
			phone_number='123-456-7890',
			email='example@example.com',
			address='1234 Address avenue',
			facebook_url='https://facebook.com',
			instagram_url='https://instagram.com',
		)
		return config

	def _superuser_access(self, url):
		self.client.login(username=self.superuser.username, password=self.password)
		response = self.client.get(url)
		return response.status_code

	def _non_superuser_access(self, url):
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(url)
		return response.status_code


class TestConfigCreate(ConfigBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = Configurations.get_create_url()

	def test_access(self):
		pass

	def test_get_request_no_config(self):
		"""On a get request, if there is no config, a form should be displayed"""
		pass

	def test_get_request_with_config(self):
		"""On a get request, if there is a config, they should be redirected to the config read page."""
		pass

	def test_post_request_with_config(self):
		"""Similar to test_get_request_with_config."""
		pass

	def test_valid_post_request_with_no_config(self):
		"""On a post request, if there is no config and the form is valid, they should be redirected to config read page."""
		pass

	def test_invalid_post_request_with_no_config(self):
		"""Similar to test_valid_post_request_with_no_config, except since the form is invalid, they remain on the create page."""
		pass


class TestConfigRead(ConfigBaseTestCase):
	def setUp(self):
		super().setUp()

	def test_access(self):
		pass

	def test_request_no_config(self):
		"""If there is no config, they are redirected to create a config."""
		pass

	def test_request_with_config(self):
		"""If there is a config, they are redirected to config read page."""
		pass


class TestConfigUpdate(ConfigBaseTestCase):
	def setUp(self):
		super().setUp()

	def test_access(self):
		pass

	def test_get_request_no_config(self):
		"""On a get request, if there is no config, they should be redirected to create a config."""
		pass

	def test_get_request_with_config(self):
		"""On a get request, if there is a config, they should be shown a form to update the config."""
		pass

	def test_post_request_no_config(self):
		"""Similar to test_get_request_no_config."""
		pass

	def test_valid_post_request_with_config(self):
		"""On a post request, if there is a config and the form is valid, they should be redirected to config read page."""
		pass

	def test_invalid_post_request_with_config(self):
		"""Similar to test_valid_post_request_with_config, except since the form is invalid, they remain on the update page."""
		pass
