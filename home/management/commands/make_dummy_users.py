from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from senior_project.env_settings import env
from senior_project.utils import get_one_hour_ago
from datetime import datetime
import warnings

warnings.filterwarnings("ignore")

User = get_user_model()


class Command(BaseCommand):
	help = 'Creates "Admin" group and "Customer" group. And creates 5 dummy admin users and 5 dummy customer users.'

	def make_groups(self):
		Group.objects.create(name="ADMIN")
		Group.objects.create(name="CUSTOMER")
		self.stdout.write(self.style.SUCCESS("Admin and Customer groups created"))

	def make_admins(self):
		admin1 = User.objects.create_user(first_name="Lando", last_name="Calrissian", username=env('ADMIN_USERNAME1'), email=env('DUMMY_EMAIL'), password=env('ADMIN_PASSWORD1'))
		admin1.last_login = get_one_hour_ago()
		admin1.date_joined = datetime(2018, 1, 15, 0, 0)
		admin1.save()

		admin2 = User.objects.create_user(first_name="Steve", last_name="Rogers", username=env('ADMIN_USERNAME2'), email=env('DUMMY_EMAIL'), password=env('ADMIN_PASSWORD2'))
		admin2.last_login = get_one_hour_ago()
		admin2.date_joined = datetime(2021, 1, 29, 0, 0)
		admin2.save()

		admin3 = User.objects.create_user(first_name="Nick", last_name="Fury", username=env('ADMIN_USERNAME3'), email=env('DUMMY_EMAIL'), password=env('ADMIN_PASSWORD3'))
		admin3.last_login = get_one_hour_ago()
		admin3.date_joined = datetime(2021, 4, 15, 0, 0)
		admin3.save()

		admin4 = User.objects.create_user(first_name="Leia", last_name="Organa", username=env('ADMIN_USERNAME4'), email=env('DUMMY_EMAIL'), password=env('ADMIN_PASSWORD4'))
		admin4.last_login = get_one_hour_ago()
		admin4.date_joined = datetime(2021, 3, 27, 0, 0)
		admin4.save()

		admin5 = User.objects.create_user(first_name="Bruce", last_name="Wayne", username=env('ADMIN_USERNAME5'), email=env('DUMMY_EMAIL'), password=env('ADMIN_PASSWORD5'))
		admin5.last_login = get_one_hour_ago()
		admin5.date_joined = datetime(2021, 7, 8, 0, 0)
		admin5.save()

		admin_group = Group.objects.get(name="ADMIN")
		admin_group.user_set.add(admin1, admin2, admin3, admin4, admin5)

		self.stdout.write(self.style.SUCCESS("5 admin users created."))

	def make_customers(self):
		# first name, last name, username,
		customer1 = User.objects.create_user(first_name="Mike", last_name="Peterson", username=env('CUSTOMER_USERNAME1'), email=env('DUMMY_EMAIL'), password=env('CUSTOMER_PASSWORD1'))
		customer1.last_login = get_one_hour_ago()
		customer1.date_joined = datetime(2022, 1, 10, 0, 0)
		customer1.save()

		customer2 = User.objects.create_user(first_name="Philippa", last_name="Georgiou", username=env('CUSTOMER_USERNAME2'), email=env('DUMMY_EMAIL'), password=env('CUSTOMER_PASSWORD2'))
		customer2.last_login = get_one_hour_ago()
		customer2.date_joined = datetime(2022, 2, 25, 0, 0)
		customer2.save()

		customer3 = User.objects.create_user(first_name="Phil", last_name="Coulson", username=env('CUSTOMER_USERNAME3'), email=env('DUMMY_EMAIL'), password=env('CUSTOMER_PASSWORD3'))
		customer3.last_login = get_one_hour_ago()
		customer3.date_joined = datetime(2024, 1, 11, 0, 0)
		customer3.save()

		customer4 = User.objects.create_user(first_name="Jemma", last_name="Simmons", username=env('CUSTOMER_USERNAME4'), email=env('DUMMY_EMAIL'), password=env('CUSTOMER_PASSWORD4'))
		customer4.last_login = get_one_hour_ago()
		customer4.date_joined = datetime(2024, 1, 1, 0, 0)
		customer4.save()

		customer5 = User.objects.create_user(first_name="Christopher", last_name="Pike", username=env('CUSTOMER_USERNAME5'), email=env('DUMMY_EMAIL'), password=env('CUSTOMER_PASSWORD5'))
		customer5.last_login = get_one_hour_ago()
		customer5.date_joined = datetime(2024, 6, 20, 0, 0)
		customer5.save()

		customer_group = Group.objects.get(name="CUSTOMER")
		customer_group.user_set.add(customer1, customer2, customer3, customer4, customer5)

		self.stdout.write(self.style.SUCCESS("5 customer users created."))

	def add_superuser_to_admin_group(self):
		admin_group = Group.objects.get(name="ADMIN")
		admin_group.user_set.add(User.objects.get(username="Admin", email=env("ADMIN_EMAIL")))
		self.stdout.write(self.style.SUCCESS("Superuser added to Admin group."))

	def handle(self, *args, **options):
		self.make_groups()
		self.make_admins()
		self.make_customers()
		self.add_superuser_to_admin_group()
