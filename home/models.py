from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.conf import settings
from django.shortcuts import reverse
from django.db.models.functions import ExtractYear
from django.db.models import Count, Sum, Q
from ckeditor.fields import RichTextField
from senior_project.utils import format_datetime
from senior_project.exceptions import MoreThanOneActiveCartError, ErrorCreatingAStripeProduct, ErrorUpdatingAStripeProduct, ErrorDeletingAStripeProduct, ErrorCreatingStripeCheckoutSession
from senior_project.constants import MONTHS
from senior_project.utils import get_full_url
from decimal import Decimal
import uuid
import stripe
import environ


env = environ.Env(
	# set casting, default value
	DEBUG=(bool, False)
)

stripe.api_key = env('STRIPE_SECRET_KEY')


# An abstract class that other models will inherit from.
class TimestampCreatorMixin(models.Model):
	"""
	creator: is assigned to the user that creates the object.
	updater: is assigned to the user that updates the object.
	created_at: stores the datetime when the object was created.
	updated_at: stores the datetime when the record was last updated.
	"""
	creator = models.ForeignKey(verbose_name="Creator", to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='%(class)s_creator')
	updater = models.ForeignKey(verbose_name="Updater", to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='%(class)s_updater')
	created_at = models.DateTimeField(verbose_name="Date created", null=True, blank=True, auto_now_add=True)
	updated_at = models.DateTimeField(verbose_name="Date updated", auto_now=True)

	def created_at_formatted(self):
		"""
		Formats the created_at datetime.
		@return: a readable date such as "September 12, 2023, at 08:19 AM"
		"""
		return format_datetime(self.created_at)

	def updated_at_formatted(self):
		"""
		Formats the updated_at datetime.
		@return: a readable date such as "September 12, 2023, at 08:19 AM"
		"""
		return format_datetime(self.updated_at)

	class Meta:
		abstract = True  # makes the model an abstract model so other models may inherit from it.
		# 'verbose_name' and 'verbose_name_plural' defines what the model should be called in the django admin site.
		verbose_name = "TimestampCreatorMixin"
		verbose_name_plural = "TimestampCreatorMixins"


class Product(TimestampCreatorMixin):
	"""
	name: the name of the product.
	description: a description of the product.
	extra_description: a WYSIWYG editor provided by the django-ckeditor package.
	price: the price of the product.
		- It must be at least $1.
	estimated_delivery_date: a date field for the estimated delivery date of the product.
	status: the product status.
		- INACTIVE: the product is not viewable or purchasable by users. The product must be INACTIVE if
			a product's stock is 0.
		- ACTIVE: opposite of INACTIVE.
	stock: the product stock.
		- A user cannot order more than what is in stock.
	stockoverflow: records the number of products ordered when the stock was 0.
		- See the documentation for more details about the logic.
	stripe_product_id: the product ID on stripe.
		- When a product is created, a product object is also created on stripe. This is necessary
			for stripe payments to work.
	stripe_price_id: the price ID on stripe.
		- Stores the price object ID that's on stripe.
	"""
	ACTIVE = 'Active'
	INACTIVE = 'Inactive'
	name = models.CharField(default='', max_length=50)
	description = models.TextField(default='', max_length=500, blank=True, null=True)
	extra_description = RichTextField(default='', blank=True, null=True)
	price = models.DecimalField(default=1, max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('1'))])
	estimated_delivery_date = models.DateField(null=True, blank=True)
	status = models.CharField(default=INACTIVE, max_length=50, choices=[(ACTIVE, ACTIVE), (INACTIVE, INACTIVE)])
	stock = models.PositiveIntegerField(default=0)
	stock_overflow = models.PositiveIntegerField(default=0)
	stripe_product_id = models.CharField(default='', max_length=50)
	stripe_price_id = models.CharField(default='', max_length=50)

	def __str__(self):
		return self.name

	@staticmethod
	def get_list_url():
		return reverse('home:home')

	@staticmethod
	def get_create_url():
		return reverse('home:product-create')

	def get_read_url(self):
		return reverse('home:product-read', kwargs={'pk': self.pk})

	def get_update_url(self):
		return reverse('home:product-update', kwargs={'pk': self.pk})

	def get_delete_url(self):
		return reverse('home:product-delete', kwargs={'pk': self.pk})

	def is_active(self):
		return self.status == Product.ACTIVE

	def is_inactive(self):
		return self.status == Product.INACTIVE

	def get_images(self):
		"""
		An abstraction for productimage_set.all()
		@return: a QuerySet of ProductImages associated with the Product.
		"""
		images = self.productimage_set.all()
		return images

	def delete_images(self):
		"""
		Deletes the images associated with the product by calling the overridden delete() method directly.
		@return: nothing.
		"""
		for image in self.get_images():
			image.delete()

	@classmethod
	def get_active_products(cls):
		"""
		@return: a QuerySet of products with status=ACTIVE.
		"""
		products = cls.objects.filter(status=cls.ACTIVE)
		return products

	def create_stripe_product_and_price_objs(self):
		"""
		Creates a stripe product and price object. And associates them with the product.
		@return: nothing, ErrorCreatingAStripeProduct() exception otherwise.
		"""
		try:
			# Create product on stripe
			stripe_product = stripe.Product.create(
				name=self.name,
				url=get_full_url(self.get_read_url())
			)

			# Associate a price with that stripe product
			stripe_price = stripe.Price.create(
				unit_amount=int(self.price * 100),
				currency="usd",
				product=stripe_product.id,
			)

			# Add the product and price ID's to the new product instance
			self.stripe_product_id = stripe_product.id
			self.stripe_price_id = stripe_price.id
			self.save()
		except:
			self.delete()
			raise ErrorCreatingAStripeProduct("An error occurred with creating a product on stripe. The product was deleted to avoid confusion and further errors.")

	@staticmethod
	def update_stripe_product_and_price_objs(updated_product):
		"""
		Updates the stripe product and stripe price objects.
		Will not update the price if no price change has occurred.
		Will not update the product from the DB if an exception happens.
		@param updated_product: the updated product from the form.
		@return: nothing, ErrorUpdatingAStripeProduct() exception otherwise.
		"""
		try:
			# Update product on stripe
			stripe_product = stripe.Product.modify(
				updated_product.stripe_product_id,
				name=updated_product.name,
				description=updated_product.description,
				url=get_full_url(updated_product.get_read_url())
			)

			# Mark the old stripe price object as inactive.
			# You can't delete a price object.
			# You cannot modify the unit_amount (price) of a price object, you have to create a new one.
			old_stripe_price = stripe.Price.retrieve(updated_product.stripe_price_id)
			# If the price has not changed, do nothing.
			if (old_stripe_price.unit_amount / 100) == updated_product.price:
				pass
			else:
				# Create a new stripe price obj
				stripe_price = stripe.Price.create(
					unit_amount=int(updated_product.price * 100),
					currency="usd",
					product=stripe_product.id
				)

				# Update the stripe product obj and set the newly created price as the default
				stripe_product = stripe.Product.modify(
					updated_product.stripe_product_id,
					default_price=stripe_price.id
				)

				# This is performed after creating a new stripe price obj and updating the product price obj
				# Because if it were the default price, then it would cause an error.
				stripe.Price.modify(
					updated_product.stripe_price_id,
					active=False
				)
				updated_product.stripe_price_id = stripe_price.id
			updated_product.stripe_product_id = stripe_product.id
			updated_product.save()  # only save the newly creating product when the stripe product was successfully updated
		except:
			raise ErrorUpdatingAStripeProduct(
				"An error occurred with updating a product on stripe. The product was not saved to avoid confusion and further errors.")

	def delete_product_and_set_stripe_product_as_inactive(self):
		"""
		Deletes the product from the DB and calls delete_images() to delete images from AWS.
		Also sets the stripe product as inactive (it's not possible to delete a stripe product).
		Will not delete the product from the DB if an exception occurs.
		@return: nothing, ErrorDeletingAStripeProduct() exception otherwise.
		"""
		try:
			# Stripe products cannot be deleted if they have price object references, which also can't be deleted.
			# Therefor the only way to "delete" them is to set them as inactive.
			stripe.Product.modify(
				self.stripe_product_id,
				active=False
			)

			self.delete_images()
			self.delete()
		except:
			raise ErrorDeletingAStripeProduct(
				"An error occurred with deleting a product on stripe. The product was not deleted.")

	def save_product_images(self):
		# todo: waiting for AWS integration
		pass

	def delete_product_images(self):
		# todo: waiting for AWS integration
		pass

	@classmethod
	def get_top_10_selling_products(cls):
		"""
		Gets the top 10 setting products and how many of each were sold.
		@return: a tuple of 2 lists. (product names, total solds).
		"""
		top_products = cls.objects.annotate(total_sold=Sum('cartitem__quantity', filter=Q(cartitem__cart__status=Cart.INACTIVE))).order_by('-total_sold')[:10]
		product_names = [product.name for product in top_products]
		total_solds = [product.total_sold if product.total_sold else 0 for product in top_products]
		return product_names, total_solds

	class Meta:
		verbose_name = 'Product'
		verbose_name_plural = 'Products'


class ProductImage(TimestampCreatorMixin):
	"""
	product: the product the image is associated with.
	image: the image.
	"""
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	image = models.ImageField(upload_to='product_images/')

	def __str__(self):
		return self.product.name + ' image'

	class Meta:
		verbose_name = 'Product image'
		verbose_name_plural = 'Product images'

	def delete(self, *args, **kwargs):
		# Delete the image file associated with this object
		self.image.delete(save=False)
		# Call the parent class's delete method to delete the object itself
		super(ProductImage, self).delete(*args, **kwargs)


class ShippingAddress(TimestampCreatorMixin):
	"""
	address: the address.
		- Ex: 6000 J St
	city: the city.
		- Ex: Sacramento
	state: the state.
		- Ex: California, or CA.
	country: the country.
		- Ex: United States.
	postal_code: the postal code.
		- Ex: 95819
	"""
	address = models.CharField(max_length=200)
	city = models.CharField(max_length=100)
	state = models.CharField(max_length=100)
	country = models.CharField(max_length=100)
	# Uses regex to check if the zip code is all digits and 5 characters long.
	postal_code = models.CharField(max_length=5, validators=[
		RegexValidator(regex=r'^\d{5}$', message="Zip code must be exactly 5 digits long.")
	])

	def __str__(self):
		return f"{self.address}, {self.city}, {self.postal_code}, {self.state}, {self.country}"

	class Meta:
		verbose_name = 'Shipping address'
		verbose_name_plural = 'Shipping addresses'


# The shopping cart.
class Cart(TimestampCreatorMixin):
	"""
	status: the cart status.
		- INACTIVE: when the user has purchased their items, the cart is set to INACTIVE.
		- ACTIVE: the cart is viewable by the user until they purchase their items.
	uuid: a unique ID for the cart.
		- Stripe requires a page to redirect to when the payment is successful.
		- Something like /success-page
		- However we will add a UUID to the URL so the user cannot simulate a payment success by visiting it
			so easily.
	shipping address: the shipping address associated with the cart.
	"""
	ACTIVE = 'Active'
	INACTIVE = 'Inactive'
	status = models.CharField(max_length=50, choices=[(ACTIVE, ACTIVE), (INACTIVE, INACTIVE)])
	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
	shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.SET_NULL, null=True, blank=True)

	def __str__(self):
		return f"Email: {self.creator.email}, Status: {self.status}, Created: {self.created_at_formatted()}"

	def get_read_url(self):
		return reverse('home:cart-read', kwargs={'pk': self.pk})

	def get_delete_url(self):
		return reverse('home:cart-delete', kwargs={'pk': self.pk})

	def is_active(self):
		return self.status == Cart.ACTIVE

	def is_inactive(self):
		return self.status == Cart.INACTIVE

	def is_empty(self):
		"""
		@return: False if no CartItems are associated with the Cart, True otherwise.
		"""
		if self.get_cartitems().exists():
			return False
		else:
			return True

	def get_cartitems(self):
		"""
		An abstraction for cartitem_set.all()
		@return: a QuerySet of CartItems associated with the cart.
		"""
		items = self.cartitem_set.all()
		return items

	def get_total_cart_price(self):
		"""
		@return: a number representing the total price of all items in the cart.
		"""
		total = 0
		for item in self.get_cartitems():
			total += item.get_total_price()
		return total

	@classmethod
	def get_active_cart_or_create_new_cart(cls, request):
		"""
		Gets the active cart of creates a new cart. Raises an error if there's more than 1 cart.
		@param request: the incoming request.
		@return: a cart instance. Or raises exceptions if an unexpected cart count occurred.
		"""
		cart = cls.objects.filter(status=cls.ACTIVE, creator=request.user)
		if cart.count() > 1:  # a user shouldn't have multiple active carts
			raise MoreThanOneActiveCartError("More than 1 active carts were found.")
		elif cart.count() == 1:  # there's an active cart associated with the user
			return cart.first()
		else:  # no active cart associated with the user exists
			return cls.objects.create(status=cls.ACTIVE, creator=request.user, updater=request.user)

	@staticmethod
	def set_cart_as_inactive(request, cart_uuid):
		"""
		Sets the active cart associated with the user as inactive.
		@param request: the incoming request.
		@param cart_uuid: the uuid associated with the cart.
		@return: nothing. Or raises exceptions if an unexpected cart count occurred.
		"""
		# First check if there are an unexpected number of active Carts associated with the user
		carts = Cart.objects.filter(status=Cart.ACTIVE, creator=request.user)
		if carts.count() > 1:  # a user shouldn't have multiple active carts
			raise MoreThanOneActiveCartError("More than 1 active carts were found.")
		if carts.count() < 1:
			raise ValueError("An unexpected total of active carts associated to a user were found.")

		# Then set the cart as inactive
		carts.filter(uuid=cart_uuid)
		if carts.count() == 1:  # there's an active cart associated with the user
			cart = carts.first()
			cart.status = Cart.INACTIVE
			cart.save()

	def set_original_price_for_all_cart_items(self):
		"""
		The user will want to know how much they originally paid for a product.
		So set the original price for each cart item in the cart to the current product price.
		@return: nothing.
		"""
		for cart_item in self.get_cartitems():
			cart_item.original_price = cart_item.product.price
			cart_item.save()

	def has_out_of_stock_or_inactive_products(self):
		"""
		Checks if the Cart has CartItems whose Product are out of stock or are inactive.
		@return: tuple of booleans.
		"""
		is_out_of_stock = False
		is_inactive = False
		for cart_item in self.get_cartitems():
			is_out_of_stock = cart_item.is_quantity_gt_stock()
			is_inactive = cart_item.is_product_inactive()
		return is_out_of_stock, is_inactive

	def get_payment_success_and_payment_cancel_url(self, request):
		"""
		Stripe needs 2 URLS for a payment to go smoothly.
		A success URL: when the payment is successful.
		A cancel URL: when the payment is canceled by the user.
		@param request: the incoming request.
		@return: a size 2 tuple containing (success_url, canceled_url)
		"""
		scheme = request.scheme  # 'http' or 'https'
		domain = request.get_host()  # domain name
		success = reverse('home:payment-success', kwargs={'cart_uuid': self.uuid})
		cancel = reverse('home:payment-cancel')
		full_success_url = f"{scheme}://{domain}{success}"
		full_canceled_url = f"{scheme}://{domain}{cancel}"
		return full_success_url, full_canceled_url

	def create_stripe_checkout_session(self, request):
		"""
		Creates a stripe checkout session.
		@return: a stripe checkout session URL, an ErrorCreatingStripeCheckoutSession() exception otherwise.
		"""
		success_url, canceled_url = self.get_payment_success_and_payment_cancel_url(request)

		# Get the cart items prices and quantity
		line_items = []
		for cart_item in self.get_cartitems():
			line_items.append(
				{
					'price': cart_item.product.stripe_price_id,
					'quantity': cart_item.quantity
				}
			)

		# try:
		checkout_session = stripe.checkout.Session.create(
			line_items=line_items,
			mode='payment',
			success_url=success_url,
			cancel_url=canceled_url,
		)
		return checkout_session.url
		# except:
		# 	raise ErrorCreatingStripeCheckoutSession("Error creating a stripe checkout session.")

	class Meta:
		verbose_name = 'Cart'
		verbose_name_plural = 'Carts'


# An item in a shopping cart.
class CartItem(TimestampCreatorMixin):
	"""
	cart: the cart the CartItem is associated with.
	product: the product the CartItem is associated with.
	original_price: stores the original price of the product.
		- If a user visits their order confirmation page later on, they will want to know what the product
			originally costed, not the new price.
	quantity: the quantity of the associated product in the user's cart.
	"""
	cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	original_price = models.DecimalField(default=0, max_digits=10, decimal_places=2)
	quantity = models.PositiveIntegerField()

	def __str__(self):
		return self.product.name

	def is_quantity_gt_stock(self):
		"""
		@return: a boolean, is CartItem quantity > Product stock?
		"""
		return self.quantity > self.product.stock

	def is_quantity_lte_stock(self):
		"""
		@return: a boolean, is CartItem quantity <= Product stock?
		"""
		return self.quantity <= self.product.stock

	def is_quantity_zero(self):
		return self.quantity == 0

	def is_product_inactive(self):
		return self.product.is_inactive()

	def get_total_price(self):
		return self.product.price * self.quantity

	def get_total_original_price(self):
		return self.original_price * self.quantity

	class Meta:
		verbose_name = 'Cart Item'
		verbose_name_plural = 'Cart Items'


class Order(TimestampCreatorMixin):
	"""
	cart: the cart the order is associated with.
	total_price: total price of the cart.
		- Calculated by adding the price of each CartItem in the cart.
	status: the order status.
		- PLACED: when the user purchases the products, the order is set to PLACED.
		- SHIPPED: set by the admin, indicates the order is being SHIPPED.
		- DELIVERED: set by the admin, indicates the order is DELIVERED.
		- CANCELED: set by the admin, indicates the order is CANCELED.
	estimated_delivery_date: set by the admin, when they expect to deliver the order.
	notes: set by the admin, order notes that the user can see on their order confirmation page
	uuid: a unique ID for the order.
		- The order confirmation page will be something like /order-confirmation/uuid
	has_errors: indicates the order has errors.
		- See the documentation regarding stockoverflow.
	"""
	PLACED = 'Placed'
	SHIPPED = 'Shipped'
	DELIVERED = 'Delivered'
	CANCELED = 'Canceled'
	CHOICES = [(PLACED, PLACED), (SHIPPED, SHIPPED), (DELIVERED, DELIVERED), (CANCELED, CANCELED)]

	cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
	total_price = models.DecimalField(max_digits=10, decimal_places=2)
	status = models.CharField(max_length=50, choices=CHOICES)
	estimated_delivery_date = models.DateField(null=True, blank=True)
	notes = models.TextField(default='', max_length=5000, blank=True, null=True)
	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
	has_errors = models.BooleanField(default=False)

	def __str__(self):
		return f"Email: {self.creator.email}, Status: {self.status}, Created: {self.created_at_formatted()}"

	@staticmethod
	def get_list_url():
		return reverse('home:order-list')

	def get_order_confirmation_url(self):
		return reverse('home:order-confirmation', kwargs={'uuid': self.uuid})

	def is_placed(self):
		return self.status == Order.PLACED

	def is_shipped(self):
		return self.status == Order.SHIPPED

	def is_delivered(self):
		return self.status == Order.DELIVERED

	def is_canceled(self):
		return self.status == Order.CANCELED

	@classmethod
	def get_users_orders(cls, user):
		"""
		@param user: the user.
		@return: a QuerySet of orders associated with the user.
		"""
		orders = cls.objects.filter(creator=user)
		return orders

	@classmethod
	def create_order(cls, cart, request):
		"""
		Creates an Order from a Cart.
		@param cart: the Cart to be associated with the Order.
		@param request: the incoming request.
		@return: nothing.
		"""
		Order.objects.create(
			cart=cart,
			total_price=cart.get_total_cart_price(),
			status=Order.PLACED,
			creator=request.user,
			updater=request.user,
		)

	def send_order_confirmation_email(self):
		# todo: waiting for SendGrid implementation.
		pass

	@classmethod
	def get_order_counts_by_month_for_year(cls, year):
		"""
		@param year: The year.
		@return: A tuple of 2 lists. The first list represents the months in a year. The second year is the total orders
			in that month.
		"""
		months_order_totals = []
		for i, month in enumerate(MONTHS):
			total = cls.objects.filter(created_at__year=year, created_at__month=i + 1).count()
			months_order_totals.append(total)
		return MONTHS, months_order_totals

	@classmethod
	def get_years_with_orders(cls):
		"""
		@return: a QuerySet of the years in which an order was created.
		"""
		orders = cls.objects.annotate(year=ExtractYear('created_at')).values_list('year', flat=True).distinct().order_by('year')
		return orders

	@classmethod
	def get_order_status_counts(cls):
		"""
		@return: a QuerySet of order statuses and counts.
			Ex: QuerySet [{'status': 'Canceled', 'total': 2}, {'status': 'Delivered', 'total': 1}]
		"""
		order_statuses = cls.objects.values('status').annotate(total=Count('id'))
		return order_statuses

	class Meta:
		verbose_name = 'Order'
		verbose_name_plural = 'Orders'


class Contact(models.Model):
	email = models.EmailField()
	subject = models.CharField(max_length=255)
	message = models.TextField()

	def __str__(self):
		return self.email


class OrderHistory(TimestampCreatorMixin):
	"""
	Displays the dates the order was placed on, number of pastries ordered,
	totals, and order numbers (for future reference for the owner)
	"""
	date = models.CharField(max_length=100)
	num_of_pastries = models.CharField(max_length=100)
	total = models.CharField(max_length=100)
	order_number = models.CharField(max_length=200)

	def __str__(self):
		return f"{self.date}, {self.num_of_pastries}, {self.total}, {self.order_number}"
