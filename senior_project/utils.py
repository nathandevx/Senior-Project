from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from functools import wraps
from datetime import date, timedelta
from senior_project.env_settings import env
import random


def format_datetime(datetime_obj):
	"""
	Formats a datetime object.
	Ex: "January 01, 2023, 06:30 AM"
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
	domain = Site.objects.get(pk=settings.SITE_ID)
	protocol = 'https' if settings.USE_HTTPS else 'http'
	return f"{protocol}://{domain}{url}"


def get_random_date():
	"""
	Gets a random date. Only used for testing, such as in make_random_data.py.
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


def superuser_or_admin_required(func):
	"""
	Checks if the user is a superuser or in the ADMIN group.
	@return: HTTP 403 if the user is not a superuser or ADMIN, nothing otherwise.
	"""
	@wraps(func)
	def check_superuser(request, *args, **kwargs):
		if request.user.is_superuser or request.user.in_admin_group():
			pass
		else:
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


def logout_required(function):
	@wraps(function)
	def wrap(request, *args, **kwargs):
		if request.user.is_authenticated:
			# Redirect to some page (e.g., homepage)
			return HttpResponseForbidden()
		else:
			return function(request, *args, **kwargs)
	return wrap


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
			new_cities.append(city.strip().lower())
	return new_cities


def get_protocol():
	""" Returns 'http' or 'https'. """
	return 'https' if settings.USE_HTTPS else 'http'


def get_domain():
	""" Gets the current domain name. """
	return Site.objects.get(pk=settings.SITE_ID)


def get_table_data(request, cls):
	"""
	Gets a model's data that is to be displayed on /report/model_name/
	@param request: the incoming request.
	@param cls: the Model class. Like Product, Order, Blog, etc.
	@return: a tuple of (a QuerySet of Blog data, string order_by)
	"""
	sort_by = request.GET.get('sort_by')
	order_by = request.GET.get('order_by', 'desc')
	status_filter = request.GET.get('status')

	posts = cls.objects.all()

	if order_by == 'asc':
		ordering = ''
	else:
		ordering = '-'

	if status_filter is not None and status_filter != 'All':
		posts = cls.objects.filter(status=status_filter)
	elif sort_by:
		posts = cls.objects.order_by(f'{ordering}{sort_by}')
	return posts, order_by


# Gets the time for 1 hour ago
def get_one_hour_ago():
	return timezone.now() - timedelta(hours=1)


def get_num_available_dummy_users(group: str):
	group = Group.objects.get(name=group)
	users = group.user_set.filter(last_login__lte=get_one_hour_ago(), is_superuser=False).order_by('last_login')
	return users.count()


def get_dummy_user(group: str):
	"""
	Returns a dummy user.
	Arranges the users based on their most recent login and attempts to get the user who logged in the longest time ago.
	If the user who logged in the longest time ago last logged in an hour ago, then it will return None.
	:param group: ADMIN or CUSTOMER
	:return: None or a User object.
	"""
	group = Group.objects.get(name=group)
	users = group.user_set.filter(is_superuser=False, last_login__lte=get_one_hour_ago()).order_by('last_login')
	if users:
		return users.first()
	else:  # there are no users that were last logged in over an hour ago
		return None


def email_num_dummy_users():
	"""
	Sends an email to the admin if the number of dummy users in use (ADMIN or CUSTOMER groups) is greater than 1.
	"""
	if settings.DEBUG is False:  # if in production
		num_admins_in_use = get_num_available_dummy_users("ADMIN")
		num_customers_in_use = get_num_available_dummy_users("CUSTOMER")
		if num_admins_in_use <= 2 or num_customers_in_use <= 2:
			send_mail("SP: Demo Users", f"{num_admins_in_use}/5 admins are available. {num_customers_in_use}/5 customers are available.", env('ADMIN_EMAIL'), [env('ADMIN_EMAIL')])
