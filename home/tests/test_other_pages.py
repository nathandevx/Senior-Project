from django.core import mail
from django.urls import resolve
from django.shortcuts import reverse
from django.contrib.auth import get_user_model
from django.forms.fields import Field
from home.models import Configurations
from home.views import views
from home.tests.base import BaseTestCase
from users.forms import DeleteUserForm
from users.views import delete_user
import environ


User = get_user_model()

env = environ.Env(
	# set casting, default value
	DEBUG=(bool, False)
)


class TestDeleteUser(BaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = User.get_delete_url()

	def test_user_access(self):
		self.client.login(username=self.user1.username, password=self.user1_password)
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)

	def test_non_logged_in_access(self):
		"""Anonymous and non-authenticated users should not be able to access the page."""
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 403)

	def test_get_request(self):
		self.client.login(username=self.user1.username, password=self.user1_password)
		response = self.client.get(self.url)
		context = response.context

		self.assertEquals(resolve(self.url).func, delete_user)
		self.assertTemplateUsed(response, 'users/delete_account.html')
		self.assertEquals(response.status_code, 200)

		self.assertIn('form', context)
		self.assertIsInstance(context['form'], DeleteUserForm)

	def test_post_request_valid_data(self):
		"""They click a checkbox and a button to delete their account."""
		self.client.login(username=self.user1.username, password=self.user1_password)
		response = self.client.post(self.url, data={'delete_checkbox': True})
		self.assertFalse(User.objects.filter(pk=self.user1.pk).exists())
		self.assertRedirects(response, reverse('home:home'), status_code=302, target_status_code=200)

	def test_post_request_invalid_data(self):
		"""They do not click the checkbox, so they're unable to delete their account."""
		self.client.login(username=self.user1.username, password=self.user1_password)
		form_data = {'delete_checkbox': False}
		response = self.client.post(self.url, data=form_data)
		self.assertTrue(User.objects.filter(pk=self.user1.pk).exists())
		self.assertFormError(DeleteUserForm(form_data), 'delete_checkbox', [Field.default_error_messages['required']])
		self.assertEquals(response.request.get('PATH_INFO'), self.url)
		self.assertEquals(response.status_code, 200)


class TestConfigurationPages(BaseTestCase):
	def setUp(self):
		super().setUp()

	def _create_objects(self):
		pass

	def test_config_create(self):
		pass

	def test_config_read(self):
		pass

	def test_config_update(self):
		pass


class TestContactPage(BaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = reverse('home:contact')

	def test_get_request(self):
		response = self.client.get(self.url)
		context = response.context

		self.assertEquals(resolve(self.url).func, views.contact)
		self.assertTemplateUsed(response, 'home/contact.html')
		self.assertEquals(response.status_code, 200)

		self.assertIn('config', context)
		self.assertEquals(context['config'], Configurations.get_first_configuration() or None)  # the config can be empty

	def test_post_request(self):
		"""They submit the form. Tests if sending an email causes problems."""
		form_data = {
			'email': env('ADMIN_EMAIL'),
			'subject': 'Email subject',
			'message': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
		}
		response = self.client.post(self.url, data=form_data)
		with self.assertRaises(Exception):
			mail.send_mail(form_data['subject'], form_data['message'], env('FROM_EMAIL'), [env('ADMIN_EMAIL')])
			self.assertEqual(len(mail.outbox), 1)
			self.assertEqual(mail.outbox[0].subject, form_data['subject'])
			self.assertEqual(mail.outbox[0].body, form_data['message'])
		self.assertRedirects(response, reverse('home:home'), status_code=302, target_status_code=200)
