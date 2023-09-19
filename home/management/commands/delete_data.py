from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from home.models import Product, ProductImage, ShippingAddress, Cart, CartItem, Order
from blog.models import Post
from senior_project.exceptions import CommandNotAllowedInProduction

User = get_user_model()


class Command(BaseCommand):
	help = 'Deletes data for the following models; Post, Product, ProductImage, ShippingAddress, Cart, CartItem, Order, Users (not superusers)'

	def handle(self, *args, **options):
		if not settings.DEBUG:  # command should not be run in production
			raise CommandNotAllowedInProduction("delete_data custom django command is not allowed to be ran in production.")

		self.stdout.write("Deleting objects: Post, Product, ProductImage, ShippingAddress, Cart, CartItem, Order, Users (not superusers)")
		Post.objects.all().delete()
		Product.objects.all().delete()
		ProductImage.objects.all().delete()
		ShippingAddress.objects.all().delete()
		Cart.objects.all().delete()
		CartItem.objects.all().delete()
		Order.objects.all().delete()
		User.objects.filter(is_superuser=False).delete()
		self.stdout.write("Objects deleted.")
