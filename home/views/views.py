from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from ..forms import ContactForm

def about(request):
    return render(request, 'home/about.html')


def blog(request):
    return render(request, 'home/blog.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            email_subject = f'New contact {form.cleaned_data["email"]}: {form.cleaned_data["subject"]}'
            email_message = form.cleaned_data['message']
            send_mail(email_subject, email_message, settings.CONTACT_EMAIL, settings.ADMIN_EMAILS)
            return render(request, 'home/success.html')
    form = ContactForm()
    context = {'form': form}
    return render(request, 'home/contact.html', context)


def home(request):
    return render(request, 'home/home.html')


def order(request):
    return render(request, 'home/order.html')


def product(request):
    return render(request, 'home/product.html')


def report(request):
    return render(request, 'home/report.html')
