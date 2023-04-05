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


# Error pages like 400, 403, 404, 500 -------------------------
def error_400(request, exception=None):  # bad request
    return render(request, 'error_pages/400.html')


def error_403(request, exception=None):  # forbidden access
    return render(request, 'error_pages/403.html')


def error_404(request, exception=None):  # page not found
    return render(request, 'error_pages/404.html')


def error_500(request, exception=None):  # server error
    return render(request, 'error_pages/500.html')
