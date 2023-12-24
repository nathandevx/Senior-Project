from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from senior_project.env_settings import env
from senior_project.utils import get_one_hour_ago

User = get_user_model()


class Command(BaseCommand):
	help = 'Creates "Admin" group and "Customer" group. And creates 5 dummy admin users and 5 dummy customer users.'

	def make_groups(self):
		Group.objects.create(name="ADMIN")
		Group.objects.create(name="CUSTOMER")
		self.stdout.write(self.style.SUCCESS("Admin and Customer groups created"))

	def make_admins(self):
		admin1 = User.objects.create_user(username=env('ADMIN_USERNAME1'), email=env('DUMMY_EMAIL'), password=env('ADMIN_PASSWORD1'))
		admin1.last_login = get_one_hour_ago()
		admin1.save()

		admin2 = User.objects.create_user(username=env('ADMIN_USERNAME2'), email=env('DUMMY_EMAIL'), password=env('ADMIN_PASSWORD2'))
		admin2.last_login = get_one_hour_ago()
		admin2.save()

		admin3 = User.objects.create_user(username=env('ADMIN_USERNAME3'), email=env('DUMMY_EMAIL'), password=env('ADMIN_PASSWORD3'))
		admin3.last_login = get_one_hour_ago()
		admin3.save()

		admin4 = User.objects.create_user(username=env('ADMIN_USERNAME4'), email=env('DUMMY_EMAIL'), password=env('ADMIN_PASSWORD4'))
		admin4.last_login = get_one_hour_ago()
		admin4.save()

		admin5 = User.objects.create_user(username=env('ADMIN_USERNAME5'), email=env('DUMMY_EMAIL'), password=env('ADMIN_PASSWORD5'))
		admin5.last_login = get_one_hour_ago()
		admin5.save()

		admin_group = Group.objects.get(name="ADMIN")
		admin_group.user_set.add(admin1, admin2, admin3, admin4, admin5)

		self.stdout.write(self.style.SUCCESS("5 admin users created successfully."))

	def make_customers(self):
		customer1 = User.objects.create_user(username=env('CUSTOMER_USERNAME1'), email=env('DUMMY_EMAIL'), password=env('CUSTOMER_PASSWORD1'))
		customer1.last_login = get_one_hour_ago()
		customer1.save()

		customer2 = User.objects.create_user(username=env('CUSTOMER_USERNAME2'), email=env('DUMMY_EMAIL'), password=env('CUSTOMER_PASSWORD2'))
		customer2.last_login = get_one_hour_ago()
		customer2.save()

		customer3 = User.objects.create_user(username=env('CUSTOMER_USERNAME3'), email=env('DUMMY_EMAIL'), password=env('CUSTOMER_PASSWORD3'))
		customer3.last_login = get_one_hour_ago()
		customer3.save()

		customer4 = User.objects.create_user(username=env('CUSTOMER_USERNAME4'), email=env('DUMMY_EMAIL'), password=env('CUSTOMER_PASSWORD4'))
		customer4.last_login = get_one_hour_ago()
		customer4.save()

		customer5 = User.objects.create_user(username=env('CUSTOMER_USERNAME5'), email=env('DUMMY_EMAIL'), password=env('CUSTOMER_PASSWORD5'))
		customer5.last_login = get_one_hour_ago()
		customer5.save()

		customer_group = Group.objects.get(name="CUSTOMER")
		customer_group.user_set.add(customer1, customer2, customer3, customer4, customer5)

		self.stdout.write(self.style.SUCCESS("5 customer users created successfully."))

	def handle(self, *args, **options):
		self.make_groups()
		self.make_admins()
		self.make_customers()
