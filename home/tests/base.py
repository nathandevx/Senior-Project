from django.contrib.auth import get_user_model
from django.test import TestCase
import environ


env = environ.Env(
	# set casting, default value
	DEBUG=(bool, False)
)

User = get_user_model()


class BaseTestCase(TestCase):
	def setUp(self):
		# Create superuser
		self.superuser = User.objects.create_superuser(username='Admin', email=env("ADMIN_EMAIL"), password='123')
		self.superuser_password = '123'

		# Create regular user
		self.user1 = User.objects.create_user(username='User 1', email='example@example.com', password='123')
		self.user1_password = '123'
