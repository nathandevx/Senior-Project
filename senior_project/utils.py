from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.http import HttpResponseForbidden
from django.utils import timezone
from functools import wraps
from datetime import date
import random
import environ


env = environ.Env(
	# set casting, default value
	DEBUG=(bool, False)
)


def format_datetime(datetime_obj):
	"""
	Formats a datetime object.
	Ex: "January 01, 2023, 06:30 AM"
	@param datetime_obj: datetime object.
	@return: a formatted datetime object.
	"""
	return timezone.localtime(datetime_obj).strftime('%B %d, %Y, %I:%M %p')


def get_full_url(url, request):
	"""
	Gets the full URL.
	@param url: an url like "product/1/"
	@return: an url like "https://localhost.com/product/1/"
	"""
	# url can be model_instance.get_read_url
	current_site_domain = get_current_site(request)
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
		if not request.user.is_authenticated:
			return HttpResponseForbidden()
		return func(request, *args, **kwargs)
	return check_login


def get_allowed_cities(test_cities=None):
	"""
	Gets the ALLOWED_CITIES and puts them into a comma separated list.
	@param test_cities: used for test cases.
	@return: a list
	"""
	if test_cities:
		cities = test_cities
	else:
		cities = env('ALLOWED_CITIES')
	cities = cities.split(',')
	new_cities = []
	for city in cities:
		if city not in ['', ',', ' ']:
			new_cities.append(city.strip())
	return new_cities


def combine_form_dicts(user, form_data: dict):
	"""
	@param user: the user.
	@param form_data: a dict.
	@return: the form_data + TimeStampCreatorMixin data in dictionary format.
	"""
	extra_data = {
		'creator': user,
		'updater': user,
		'created_at': timezone.now(),
		'updated_at': timezone.now(),
	}
	# form_data + data
	return {**form_data, **extra_data}
