from django.core.mail import send_mail
from django.shortcuts import redirect, render, reverse
from django.contrib import messages
from home.forms import ContactForm
from home.models import Product
import environ

env = environ.Env(
	# set casting, default value
	DEBUG=(bool, False)
)


def contact(request):
	if not request.user.is_authenticated:
		messages.info(request, 'Login to use the contact form.')
		return redirect(reverse('account_login'))
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			subject = form.cleaned_data['subject']
			message = form.cleaned_data['message']
			send_mail("Contact form: " + subject, f" \nFrom: {email}\n\n" + message, env('ADMIN_EMAIL'), [env('ADMIN_EMAIL')])
			return redirect('home:home')
	return render(request, 'home/contact.html')


def home(request):
	products = Product.get_active_products()
	return render(request, 'home/home.html', {'products': products})

