from django.contrib import admin
from .models import Product, ProductImage, ShippingAddress, Cart, CartItem, Order, OrderHistory


admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ShippingAddress)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderHistory)
