from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from home.models import Product, ShippingAddress, Cart, CartItem, Order, OrderHistory
from blog.models import Post

User = get_user_model()


class Command(BaseCommand):
	help = 'Deletes data for the following models; Post, Product, ProductImage, ShippingAddress, Cart, CartItem, Order, Contact, OrderHistory, Groups, Users (not superusers)'

	def handle(self, *args, **options):
		self.stdout.write("Deleting objects: Post, Product, ProductImage, ShippingAddress, Cart, CartItem, Order, Contact, OrderHistory, Groups, Users (not superusers)")
		Post.objects.all().delete()
		# Delete ProductImages and Products
		for product in Product.objects.all():
			product.delete_images()
			product.delete()
		ShippingAddress.objects.all().delete()
		Cart.objects.all().delete()
		CartItem.objects.all().delete()
		Order.objects.all().delete()
		OrderHistory.objects.all().delete()
		User.objects.filter(is_superuser=False).delete()
		Group.objects.all().delete()
		self.stdout.write("Objects deleted.")
