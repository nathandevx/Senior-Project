from django.forms import ModelForm
from .models import Contact
from django import forms
from .models import Product

class ContactForm(ModelForm):
    class Meta:
        model = Contact
        fields = '__all__'



class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__' 
 # This means all fields from the Product model will be included in the form.

