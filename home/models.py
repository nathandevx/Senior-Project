from django.core.validators import RegexValidator, MinValueValidator
from django.db import models
from django.conf import settings
from ckeditor.fields import RichTextField
from decimal import Decimal
from senior_project.utils import format_datetime
import uuid


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
		"""
		Makes the model an abstract model so other models may inherit from it.

		verbose_name and verbose_name_plural defines what the model should be called in the django admin site.
		"""
		abstract = True
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
	cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
	total_price = models.DecimalField(max_digits=10, decimal_places=2)
	status = models.CharField(max_length=50, choices=[(PLACED, PLACED), (SHIPPED, SHIPPED), (DELIVERED, DELIVERED), (CANCELED, CANCELED)])
	estimated_delivery_date = models.DateField(null=True, blank=True)
	notes = models.TextField(default='', max_length=5000, blank=True, null=True)
	uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
	has_errors = models.BooleanField(default=False)

	def __str__(self):
		return f"Email: {self.creator.email}, Status: {self.status}, Created: {self.created_at_formatted()}"

	class Meta:
		verbose_name = 'Order'
		verbose_name_plural = 'Orders'

class Contact(models.Model):
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()

    def __str__(self):
        return self.email