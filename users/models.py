from django.contrib.auth.models import AbstractUser
from django.db.models.functions import ExtractYear
from django.shortcuts import reverse
from senior_project.constants import MONTHS
from home.models import Order, ShippingAddress


class User(AbstractUser):
	@staticmethod
	def get_delete_url():
		return reverse('users:delete-user')

	@classmethod
	def get_total_year_users(cls, year):
		"""
		For the given year, find how many users joined each month of that year.
		@param year: the year.
		@return: a tuple of (months, month_user_counts).
		"""
		month_user_counts = []
		for i, month in enumerate(MONTHS):
			total = cls.objects.filter(date_joined__year=year, date_joined__month=i + 1).count()
			month_user_counts.append(total)
		return MONTHS, month_user_counts

	@classmethod
	def get_years_with_users(cls):
		"""
		Gets the years when there was at least 1 user that joined.
		@return: a list of years in ASC order where at least 1 user joined.
		"""
		users = cls.objects.annotate(year_joined=ExtractYear('date_joined')).values_list('year_joined', flat=True).distinct().order_by('year_joined')
		return users

	@classmethod
	def get_customers(cls):
		return cls.objects.filter(is_superuser=False, is_staff=False)

	def get_users_shipping_addresses(self):
		return ShippingAddress.objects.filter(creator=self)

	def has_order(self):
		"""Returns true if a user has an order, false otherwise """
		return Order.objects.filter(creator=self).count() > 0
