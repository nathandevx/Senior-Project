from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files import File
from django.conf import settings
from faker import Faker
from home.models import Product, ProductImage, ShippingAddress, Cart, CartItem, Order
from blog.models import Post
from senior_project.exceptions import CommandNotAllowedInProduction
from senior_project.utils import get_random_date
import random
import uuid
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
			username=faker.user_name(),
			email=faker.email(),
			password=faker.password(),
			date_joined=get_random_date()
		)
		return user

	@staticmethod
	def create_random_product(creator):
		product = Product.objects.create(
			name=faker.word(),
			description=faker.sentence(),
			price=random.uniform(10, 200),
			estimated_delivery_date=get_random_date(),
			status=random.choice([Product.ACTIVE, Product.INACTIVE]),
			stock=random.randint(1, 5),
			stripe_product_id=str(uuid.uuid4()),
			stripe_price_id=str(uuid.uuid4()),
			creator=creator,
			updater=creator
		)
		return product

	@staticmethod
	def create_random_product_image(product, creator):
		with open('static/images/pastry1.jpeg', 'rb') as image_file:
			product_image = ProductImage.objects.create(
				product=product,
				image=File(image_file),
				creator=creator,
				updater=creator
			)

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
			updater=creator
		)
		return address

	@staticmethod
	def create_random_cart(creator, shipping_address):
		cart = Cart.objects.create(
			status=Cart.INACTIVE,
			shipping_address=shipping_address,
			creator=creator,
			updater=creator
		)
		return cart

	@staticmethod
	def create_random_cart_item(cart, product, creator):
		cart_item = CartItem.objects.create(
			cart=cart,
			product=product,
			quantity=random.randint(1, 20),
			original_price=product.price,
			creator=creator,
			updater=creator
		)
		return cart_item

	def create_random_order(self, cart, creator):
		order = Order.objects.create(
			cart=cart,
			total_price=cart.get_total_cart_price(),
			status=random.choice([Order.PLACED, Order.SHIPPED, Order.DELIVERED, Order.CANCELED]),
			creator=creator,
			updater=creator,
		)
		return order

	@staticmethod
	def create_random_blog_posts(creator):
		post = Post.objects.create(
			title=faker.word(),
			preview_text=faker.sentence(),
			content=faker.sentence(),
			status=Post.ACTIVE,
			creator=creator,
			updater=creator,
			created_at=get_random_date()
		)
		return post

	def add_arguments(self, parser):
		parser.add_argument('--count', type=int, default=5, help='Number of objects to create.')

	# Define logic of command
	def handle(self, *args, **options):
		if not settings.DEBUG:
			raise CommandNotAllowedInProduction("make_data custom django command is not allowed to be ran in production.")

		self.stdout.write("Making data..")
		count = options['count']

		# Make products
		for i, _ in enumerate(range(count*2)):
			product = self.create_random_product(superuser)
			self.create_random_product_image(product, superuser)
			self.stdout.write(f"{i+1}/{count*2} count of product objects created.")

		all_products = list(Product.objects.all())
		# Make users, addresses, carts, cart items, orders,
		for i, _ in enumerate(range(count)):
			user = self.create_random_user()
			address = self.create_random_shipping_address(user)
			cart = self.create_random_cart(user, address)
			self.create_random_blog_posts(user)

			# Make cart items
			for _ in range(random.randrange(4)):  # 0-3 (not including 4)
				self.create_random_cart_item(cart, random.choice(all_products), user)
			order = self.create_random_order(cart, user)
			order.created_at = get_random_date()
			order.save()
			self.stdout.write(f"{i+1}/{count} count of other objects created.")

		self.stdout.write("Objects created.")
