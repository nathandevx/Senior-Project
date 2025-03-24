from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.contrib.sites.models import Site
from django.conf import settings
from django.test import TestCase
import environ


env = environ.Env(
	# set casting, default value
	DEBUG=(bool, False)
)

User = get_user_model()


class BaseTestCase(TestCase):
	def setUp(self):
		admin_group = Group.objects.create(name='ADMIN')

		# The default password
		self.password = '123'

		# Create superuser
		self.superuser = User.objects.create_superuser(username='Admin', email=env("ADMIN_EMAIL"), password=self.password)
		self.superuser_password = self.password
		admin_group.user_set.add(self.superuser)

		# Create regular users
		self.user1 = User.objects.create_user(username='User 1', email='example@example.com', password=self.password)
		self.user1_password = self.password
		self.user2 = User.objects.create_user(username='User 2', email='example@example.com', password=self.password)

		# Create anonymous users
		self.anonymous_user = AnonymousUser()

		# The default site is example.com, change it to 127.0.0.1:8000
		site = Site.objects.filter(pk=settings.SITE_ID).first()
		site.domain = "127.0.0.1:8000"
		site.name = "127.0.0.1:8000"
		site.save()

		# The site's domain name, ex: example.com.
		self.domain = Site.objects.get(pk=settings.SITE_ID).domain
		# The site's protocol, ex: http or https
		self.protocol = 'https' if settings.USE_HTTPS else 'http'

	def _superuser_login(self):
		self.client.login(username=self.superuser.username, password=self.superuser_password)

	def _user1_login(self):
		self.client.login(username=self.user1.username, password=self.user1_password)
