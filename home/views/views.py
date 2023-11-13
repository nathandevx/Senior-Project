from django.core.mail import send_mail
from django.shortcuts import redirect, render
from senior_project.utils import superuser_required
from home.forms import ContactForm
from home.models import Product, Configurations, Order
import environ

env = environ.Env(
	# set casting, default value
	DEBUG=(bool, False)
)


def about(request):
	return render(request, 'home/about.html')


def contact(request):
	config = Configurations.get_first_configuration()
	if request.method == 'POST':
		form = ContactForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			subject = form.cleaned_data['subject']
			message = form.cleaned_data['message']
			send_mail("Contact form: " + subject, f" \nFrom: {email}\n\n" + message, env('ADMIN_EMAIL'), [env('ADMIN_EMAIL')])
			return redirect('home:home')
	return render(request, 'home/contact.html', {"config": config})


def home(request):
	products = Product.get_active_products()
	is_superuser = request.user.is_superuser
	return render(request, 'home/home.html', {'products': products, 'is_superuser': is_superuser})


def order(request):
	return render(request, 'home/order.html')


def product(request):
	return render(request, 'home/product.html')


@superuser_required
def report(request):
	months, order_counts = Order.get_year_months_total_orders(2023)
	status_counts = Order.get_order_statuses()
	order_status = list(status_counts.values_list('status', flat=True))
	order_total = list(status_counts.values_list('total', flat=True))
	return render(request, 'home/report.html', {'months': months, 'order_counts': order_counts, 'order_status': order_status, 'order_total': order_total})


def cart_demo(request):
	return render(request, 'home/addtocart.html')
