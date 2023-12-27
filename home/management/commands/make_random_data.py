from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files import File
from faker import Faker
from home.models import Product, ProductImage, ShippingAddress, Cart, CartItem, Order
from blog.models import Post
from senior_project.utils import get_random_date
from senior_project import constants
import random
import warnings

warnings.filterwarnings("ignore")


faker = Faker()
User = get_user_model()
superuser = User.objects.filter(is_superuser=True).first()


class Command(BaseCommand):
	help = (
		'Makes data for the following models; Post, Product, ProductImage, ShippingAddress, Cart, CartItem, Order. '
		'Will not work if you\'d like to checkout using the product since stripe_product_id and stripe_price_id are not valid.'
		'Random "created_at" dates will not work unless TimestampCreatorMixin class\'s created_at field has editable=True and dose not have auto_now_add=True.'
	)

	@staticmethod
	def create_random_user():
		user = User.objects.create_user(
			first_name=faker.first_name(),
			last_name=faker.last_name(),
			username=faker.user_name(),
			email=faker.email(),
			password=faker.password(),
			date_joined=get_random_date()
		)
		return user

	@staticmethod
	def create_random_product(creator, i):
		product = Product.objects.create(
			name=f"P{i+1}",
			description=constants.LOREM_20,
			price=random.uniform(10, 100),
			estimated_delivery_date=get_random_date(),
			status=random.choice([Product.ACTIVE, Product.INACTIVE]),
			stock=random.randint(1, 20),
			creator=creator,
			updater=creator,
		)
		product.created_at = get_random_date()
		product.updated_at = get_random_date()
		product.save()
		product.create_stripe_product_and_price_objs()
		return product

	@staticmethod
	def create_random_product_image(product, creator):
		with open('static/images/dummy_image1.jpg', 'rb') as image_file:
			product_image = ProductImage.objects.create(
				product=product,
				image=File(image_file),
				creator=creator,
				updater=creator,
			)
			product_image.created_at = get_random_date()
			product_image.updated_at = get_random_date()
			product_image.save()
		return product_image

	@staticmethod
	def create_random_shipping_address(creator):
		address = ShippingAddress.objects.create(
			address=faker.street_address(),
			city=faker.city(),
			state=faker.state(),
			country=faker.country(),
			postal_code=random.randint(10000, 99999),
			creator=creator,
			updater=creator,
		)
		address.created_at = get_random_date()
		address.updated_at = get_random_date()
		address.save()
		return address

	@staticmethod
	def create_random_cart(creator, shipping_address):
		cart = Cart.objects.create(
			status=Cart.INACTIVE,
			shipping_address=shipping_address,
			creator=creator,
			updater=creator
		)
		cart.created_at = get_random_date()
		cart.updated_at = get_random_date()
		cart.save()
		return cart

	@staticmethod
	def create_random_cart_item(cart, product, creator):
		cart_item = CartItem.objects.create(
			cart=cart,
			product=product,
			quantity=random.randint(1, 20),
			original_price=product.price,
			creator=creator,
			updater=creator,
		)
		cart_item.created_at = get_random_date()
		cart_item.updated_at = get_random_date()
		cart_item.save()
		return cart_item

	@staticmethod
	def create_random_order(cart, creator):
		order = Order.objects.create(
			cart=cart,
			total_price=cart.get_total_cart_price(),
			status=random.choice([Order.PLACED, Order.SHIPPED, Order.DELIVERED, Order.CANCELED]),
			creator=creator,
			updater=creator,
		)
		order.created_at = get_random_date()
		order.updated_at = get_random_date()
		order.save()
		return order

	@staticmethod
	def create_random_blog_posts(creator, i):
		post = Post.objects.create(
			title=f"B{i+1}",
			preview_text=constants.LOREM_50,
			content=constants.LOREM_500,
			status=random.choice([Post.ACTIVE, Post.INACTIVE]),
			creator=creator,
			updater=creator,
		)
		post.created_at = get_random_date()
		post.updated_at = get_random_date()
		post.save()
		return post

	def add_arguments(self, parser):
		parser.add_argument('--count', type=int, default=5, help='Number of objects to create.')

	# Define logic of command
	def handle(self, *args, **options):
		self.stdout.write("Making data..")
		count = options['count']

		# Make products
		for i, _ in enumerate(range(count*2)):
			product = self.create_random_product(superuser, i)
			self.create_random_product_image(product, superuser)
			self.stdout.write(f"{i+1}/{count*2} count of product objects created.")

		all_products = list(Product.objects.all())
		# Make users, addresses, carts, cart items, orders,
		for i, _ in enumerate(range(count)):
			user = self.create_random_user()
			address = self.create_random_shipping_address(user)
			cart = self.create_random_cart(user, address)
			self.create_random_blog_posts(user, i)

			# Make cart items
			for _ in range(random.randrange(4)):  # 0-3 (not including 4)
				self.create_random_cart_item(cart, random.choice(all_products), user)
			self.create_random_order(cart, user)
			self.stdout.write(f"{i+1}/{count} count of other objects created.")

		self.stdout.write("Objects created.")
