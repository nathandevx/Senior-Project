from django.test import TestCase
from django.core.mail import send_mail
import environ

env = environ.Env(
	# set casting, default value
	DEBUG=(bool, False)
)


class TestEmail(TestCase):

	def setUp(self):
		print('Test cases will now begin')

	def test_successful_email(self):
		subject = 'TestCase Subject'
		message = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.'
		try:
			send_mail(subject, message, env('FROM_EMAIL'), [env('ADMIN_EMAIL')])
			print('Email was sent successfully!')
		except:
			print('Email did not send successfully')
