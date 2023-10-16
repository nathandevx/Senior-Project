from django.shortcuts import render
from django.http import HttpResponseForbidden
from senior_project.utils import superuser_required
from ..models import Product
from ..forms import ProductForm
from django.shortcuts import render, redirect, get_object_or_404



@superuser_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            # You can integrate the stripe logic here if needed
            return redirect(product.get_read_url())  # redirecting to product detail page
    else:
        form = ProductForm()
    return render(request, 'home/product/create.html', {'form': form})


def product_read(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'home/product/read.html', {'product': product})


@superuser_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            product = form.save()
            # You can integrate the stripe logic here if needed
            return redirect(product.get_read_url())  # redirecting to product detail page
    else:
        form = ProductForm(instance=product)
    return render(request, 'home/product/update.html', {'form': form, 'product': product})



@superuser_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete_product_and_set_stripe_product_as_inactive()  # This method handles your custom deletion logic
        return redirect('home:product-list')
    return render(request, 'home/product/delete.html', {'product': product})


