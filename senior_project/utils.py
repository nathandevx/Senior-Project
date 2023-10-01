from django.utils import timezone
from django.contrib.sites.models import Site
from django.conf import settings
from django.http import HttpResponseForbidden
from functools import wraps
from datetime import date
import random


def format_datetime(datetime_obj):
	"""
	Formats a datetime object.
	Ex: "September 12, 2023, at 08:19 AM"
	@param datetime_obj: datetime object.
	@return: a formatted datetime object.
	"""
	return timezone.localtime(datetime_obj).strftime('%B %d, %Y, %I:%M %p')


def get_full_url(url):
	"""
	Gets the full URL.
	@param url: an url like "product/1/"
	@return: an url like "https://localhost.com/product/1/"
	"""
	# url can be model_instance.get_read_url
	current_site_domain = Site.objects.get(pk=1).domain
	protocol = 'https' if settings.USE_HTTPS else 'http'
	return f"{protocol}://{current_site_domain}{url}"


def get_random_date():
	"""
	Gets a random date. Only used for testing, such as in make_data.py.
	@return: a random date.
	"""
	random_month = random.randint(1, 12)
	if random_month in [1, 3, 5, 7, 8, 10, 12]:
		random_day = random.randint(1, 31)
	elif random_month == 2:
		random_day = random.randint(1, 28)  # Assuming 2023 is not a leap year
	else:
		random_day = random.randint(1, 30)
	random_year = random.randint(2020, 2050)
	random_date = date(random_year, random_month, random_day)
	return random_date


def superuser_required(func):
	"""
	Checks if the user is a superuser.
	@return: HTTP 403 if the user is not a superuser, nothing otherwise.
	"""
	@wraps(func)
	def check_superuser(request, *args, **kwargs):
		if not request.user.is_superuser:
			return HttpResponseForbidden()
		return func(request, *args, **kwargs)
	return check_superuser


def login_required(func):
	"""
	Checks if the user is logged in.
	@return: HTTP 403 if user is not logged in, nothing otherwise.
	"""
	@wraps(func)
	def check_login(request, *args, **kwargs):
		if not request.user.is_superuser:
			return HttpResponseForbidden()
		return func(request, *args, **kwargs)
	return check_login
