from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.contrib import messages
from django.http import HttpResponseForbidden
from senior_project.utils import superuser_or_admin_required
from home.models import Product, Cart
from home.forms import ProductForm, ProductImageForm, QuantityForm


@superuser_or_admin_required
def product_create(request):
	if request.method == 'POST':
		product_form = ProductForm(request.POST)
		product_image_form = ProductImageForm(request.POST, request.FILES)
		if product_form.is_valid() and product_image_form.is_valid():
			product = product_form.save(commit=False)
			product.creator = request.user
			product.updater = request.user
			product.save()

			product.create_stripe_product_and_price_objs()
			product.save_images(request.FILES.getlist('image'))

			messages.success(request, f'Successfully created product: {product.name}')
			return redirect(Product.get_list_url())
	else:
		product_form = ProductForm()
		product_image_form = ProductImageForm()

	context = {
		'product_model': Product,
		'product_form': product_form,
		'product_image_form': product_image_form,
	}
	return render(request, 'home/products/create.html', context)


def product_read(request, pk):
	product = get_object_or_404(Product, pk=pk)

	# Only superusers should be able to view inactive products
	if product.is_inactive() and not request.user.in_admin_group():
		return HttpResponseForbidden()

	if request.method == 'POST':
		# If user is not logged in, tell them they need an account and redirect them to signup page
		if not request.user.is_authenticated:
			messages.warning(request, 'Login to add items to your cart and make a (pretend) purchase.')
			return redirect(reverse('account_login'))

		# Handle add to cart button
		form = QuantityForm(request.POST)
		if form.is_valid():
			quantity = form.cleaned_data['quantity']
			cart = Cart.get_active_cart_or_create_new_cart(request.user)
			product.add_product_to_cart(request.user, cart, quantity)
			return redirect(cart.get_read_url())
	else:
		form = QuantityForm()
	return render(request, 'home/products/read.html', {'product': product, 'form': form})


@superuser_or_admin_required
def product_update(request, pk):
	product = get_object_or_404(Product, pk=pk)

	if request.method == 'POST':
		product_form = ProductForm(request.POST, request.FILES, instance=product)
		product_image_form = ProductImageForm(request.POST, request.FILES, require_images=False)

		if product_form.is_valid() and product_image_form.is_valid():
			# Product form
			updated_product = product_form.save(commit=False)
			updated_product.updater = request.user
			updated_product.save()

			# Update stripe stuff
			updated_product.update_stripe_product_and_price_objs()

			# Delete previous product images if they uploaded new images
			if request.FILES.getlist('image'):
				updated_product.delete_images()

			# Save new images
			updated_product.save_images(request.FILES.getlist('image'))

			messages.success(request, f'Successfully updated product: {updated_product.name}')
			return redirect(Product.get_list_url())
	else:
		product_form = ProductForm(instance=product)
		product_image_form = ProductImageForm(require_images=False)

	context = {
		'product_form': product_form,
		'product_image_form': product_image_form,
		'product': product,
	}
	return render(request, 'home/products/update.html', context)


@superuser_or_admin_required
def product_delete(request, pk):
	product = get_object_or_404(Product, pk=pk)
	if request.method == "POST":
		product.delete_product_and_set_stripe_product_as_inactive()
		return redirect(product.get_list_url())
	return render(request, 'home/products/delete.html', {'product': product})
