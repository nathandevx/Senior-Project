from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from senior_project.utils import get_allowed_cities
from senior_project import constants
from home.models import Product, ProductImage, CartItem, ShippingAddress, Order


class ContactForm(forms.Form):
	email = forms.EmailField()
	subject = forms.CharField(max_length=255)
	message = forms.CharField(widget=forms.Textarea)


class ProductForm(forms.ModelForm):
	# If stock_overflow > 0 then display this field so the admin can deal with it
	def __init__(self, *args, **kwargs):
		super(ProductForm, self).__init__(*args, **kwargs)
		# Check if instance exists to not cause an error
		# If the stock_overflow is 0 then don't display the field
		if self.instance and self.instance.stock_overflow == 0:
			self.fields.pop('stock_overflow')

	def clean(self):
		cleaned_data = super().clean()

		# Get stock, stock_overflow, status values
		stock = cleaned_data.get("stock")
		stock_overflow = cleaned_data.get("stock_overflow")
		status = cleaned_data.get("status")

		# The product can't be active if there is no stock
		if stock == 0 and status == Product.ACTIVE:
			raise ValidationError({
				'status': constants.PRODUCT_FORM_ERROR1
			})
		# stock_overflow is an optional parameter if it's 0.
		if stock_overflow:
			# A product cannot have stock overflow and be active
			if stock_overflow > 0 and status == Product.ACTIVE:
				raise ValidationError({
					'status': constants.PRODUCT_FORM_ERROR2
				})
		return cleaned_data

	class Meta:
		model = Product
		fields = ['name', 'description', 'extra_description', 'price', 'estimated_delivery_date', 'status', 'stock', 'stock_overflow']
		widgets = {
			# Accept multiple image file uploads
			'image': forms.ClearableFileInput(attrs={'allow_multiple_selected': True}),
			# Define how the date should be formatted, and add a HTML placeholder
			'estimated_delivery_date': forms.DateInput(format='%m/%d/%Y', attrs={'placeholder': 'mm/dd/yyyy'}),
		}


class ProductImageForm(forms.ModelForm):
	image = forms.ImageField(label='images', widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': 'multiple'}))

	def __init__(self, *args, **kwargs):
		# Add a custom parameter to the form that indicates if the form should require images. Default to true.
		require_images = kwargs.pop('require_images', True)
		super(ProductImageForm, self).__init__(*args, **kwargs)
		# Set the image field required to whatever was assigned
		self.fields['image'].required = require_images

	class Meta:
		model = ProductImage
		fields = ['image']


class QuantityForm(forms.Form):
	quantity = forms.IntegerField(validators=[MinValueValidator(1)])

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['quantity'].initial = 1


class CartItemForm(forms.ModelForm):
	class Meta:
		model = CartItem
		fields = ['quantity']


class ShippingAddressForm(forms.ModelForm):
	class Meta:
		model = ShippingAddress
		fields = ['address', 'city', 'state', 'country', 'postal_code']

	def clean_city(self):
		city = self.cleaned_data.get('city')
		if city.lower() not in get_allowed_cities():
			print(get_allowed_cities())
			raise ValidationError(constants.SHIPPING_ADDRESS_FORM_ERROR)
		return city


class OrderForm(forms.ModelForm):
	class Meta:
		model = Order
		fields = ['status', 'estimated_delivery_date', 'notes']
		widgets = {
			'estimated_delivery_date': forms.DateInput(format='%m/%d/%Y', attrs={'placeholder': 'mm/dd/yyyy'}),
		}

	def clean(self):
		cleaned_data = super().clean()
		status = cleaned_data.get("status")
		estimated_delivery_date = cleaned_data.get("estimated_delivery_date")

		if status == Order.CANCELED and estimated_delivery_date is not None:
			raise ValidationError({
				'estimated_delivery_date': constants.ORDER_FORM_ERROR
			})

		return cleaned_data
