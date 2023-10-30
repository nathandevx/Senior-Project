from django.shortcuts import render, redirect, get_object_or_404
from django.forms import modelformset_factory
from django.http import HttpResponseForbidden
from django.contrib import messages
from senior_project.utils import login_required
from home.models import Product, Cart, CartItem
from home.forms import CartItemForm


@login_required
def cart_read(request, pk):
	cart = get_object_or_404(Cart, pk=pk)

	access = cart.not_creator_or_inactive_cart(request.user)
	if access:
		return HttpResponseForbidden()

	# A set of CartItem forms
	CartItemFormSet = modelformset_factory(CartItem, form=CartItemForm, can_delete=True, extra=0)

	if request.method == 'POST':
		formset = CartItemFormSet(request.POST, prefix='cartitem', queryset=cart.get_cartitems())

		# Check if any cart item's quantity is more than the product stock
		for form in formset:
			if form.is_valid():
				if form.instance.is_quantity_gt_stock():
					form.add_error('quantity', f"Only {form.instance.product.stock} items of {form.instance.product.name} in stock!")

		# If all CartItem forms are valid
		if formset.is_valid():
			instances = formset.save(commit=False)
			# Update the 'updater' field of each instance
			for instance in instances:
				instance.updater = request.user
				instance.save()

			# Delete objects that were marked for deletion with the checkbox
			for instance in formset.deleted_objects:
				instance.delete()

			return redirect(cart.get_read_url())
	else:
		formset = CartItemFormSet(prefix='cartitem', queryset=cart.get_cartitems())

		# Compare each cart item quantity to product stock
		for form in formset:
			if form.instance.is_quantity_gt_stock():
				messages.warning(request, f"Quantity adjusted for {form.instance.product.name}. Only {form.instance.product.stock} items available. Reduced items from {form.instance.quantity} to {form.instance.product.stock}.")
				form.instance.quantity = form.instance.product.stock
				form.instance.save()
			if form.instance.is_quantity_zero():
				messages.warning(request, f"{form.instance.product.name} product removed. A cart cannot contain an item with 0 quantity.")
				form.instance.delete()
			if form.instance.is_product_inactive():
				messages.warning(request, f"{form.instance.product.name} product removed. The product is inactive.")
				form.instance.delete()

	# Add cart item data to context. Such as the form, original price, etc.
	cart_items_data = []
	for form, item in zip(formset, cart.get_cartitems()):
		cart_items_data.append({
			'form': form,
			'original_quantity': item.quantity,
			'original_price': item.product.price
		})

	context = {
		'cart': cart,
		'formset': formset,
		'cart_items_data': cart_items_data,
	}
	return render(request, 'home/carts/read.html', context)


@login_required
def cart_delete(request, pk):
	cart = get_object_or_404(Cart, pk=pk)

	access = cart.not_creator_or_inactive_cart(request.user)
	if access:
		return HttpResponseForbidden()

	if request.method == "POST":
		cart.delete()
		return redirect(Product.get_list_url())

	context = {
		'cart': cart,
	}
	return render(request, 'home/carts/delete.html', context)