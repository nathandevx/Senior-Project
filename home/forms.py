from django.core.exceptions import ValidationError
from django import forms
from .models import CartItem, Product, ShippingAddress, Contact, Configurations
from senior_project.utils import get_allowed_cities


class ContactForm(forms.ModelForm):
	class Meta:
		model = Contact
		fields = '__all__'


class CartItemForm(forms.ModelForm):
	class Meta:
		model = CartItem
		fields = ['quantity']


class ProductForm(forms.ModelForm):
	class Meta:
		model = Product
		fields = '__all__'


class ShippingAddressForm(forms.ModelForm):
	class Meta:
		model = ShippingAddress
		fields = ['address', 'city', 'state', 'country', 'postal_code']

	def clean_city(self):
		city = self.cleaned_data.get('city')
		if city.lower() not in get_allowed_cities():
			raise ValidationError(f"We only deliver to the following cities: {', '.join(get_allowed_cities())}")
		return city


class ConfigurationForm(forms.ModelForm):
	class Meta:
		model = Configurations
		fields = '__all__'