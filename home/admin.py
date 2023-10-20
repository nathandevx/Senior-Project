from django.contrib import admin
from django.conf import settings
from .models import Product, ProductImage, ShippingAddress, Cart, CartItem, Order, Contact, OrderHistory, Configurations


admin.site.register(Configurations)

# The models shouldn't be editable via admin in production
if settings.DEBUG:  # if in development
	admin.site.register(Product)
	admin.site.register(ProductImage)
	admin.site.register(ShippingAddress)
	admin.site.register(Cart)
	admin.site.register(CartItem)
	admin.site.register(Order)
	admin.site.register(Contact)
	admin.site.register(OrderHistory)
