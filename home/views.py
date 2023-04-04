from django.shortcuts import render


def about(request):
    return render(request, 'home/about.html')


def blog(request):
    return render(request, 'home/blog.html')


def contact(request):
    return render(request, 'home/contact.html')


def home(request):
    return render(request, 'home/home.html')


def order(request):
    return render(request, 'home/order.html')


def product(request):
    return render(request, 'home/product.html')


def report(request):
    return render(request, 'home/report.html')
