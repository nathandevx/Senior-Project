from django.urls import resolve
from senior_project import constants
from home.tests.base import BaseTestCase
from home.models import Product, ProductImage, CartItem, Cart
from home.views import products
from home.forms import ProductForm, ProductImageForm, QuantityForm


class ProductBaseTestCase(BaseTestCase):
	def setUp(self):
		super().setUp()
		self.active_product = Product.objects.create(
			name='p1',
			description='description1',
			price=10,
			status=Product.ACTIVE,
			stock=10,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.inactive_product = Product.objects.create(
			name='p2',
			description='description2',
			price=20,
			status=Product.INACTIVE,
			stock=20,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.active_product.create_stripe_product_and_price_objs()
		self.inactive_product.create_stripe_product_and_price_objs()


class TestProductCreate(ProductBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = Product.get_create_url()

	def test_superuser_access(self):
		self.client.login(username=self.superuser.username, password=self.password)
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)

	def test_user_access(self):
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 403)

	def test_get_request(self):
		self.client.login(username=self.superuser.username, password=self.password)
		response = self.client.get(self.url)
		context = response.context

		self.assertEquals(resolve(self.url).func, products.product_create)
		self.assertTemplateUsed(response, 'home/products/create.html')
		self.assertEquals(response.status_code, 200)

		self.assertIn('product_model', context)
		self.assertIn('product_form', context)
		self.assertIn('product_image_form', context)

		self.assertEquals(context['product_model'], Product)
		self.assertIsInstance(context['product_form'], ProductForm)
		self.assertIsInstance(context['product_image_form'], ProductImageForm)

	def test_post_request_valid_data(self):
		self.client.login(username=self.superuser.username, password=self.password)
		initial_product_count = Product.objects.count()
		initial_product_image_count = ProductImage.objects.count()
		with open('static/images/for_testing/dummy_image1.jpg', 'rb') as file:
			form_data = {
				'name': 'valid p1',
				'price': 10,
				'status': Product.ACTIVE,
				'stock': 10,
				'image': file,
			}
			response = self.client.post(self.url, data=form_data)

		self.assertEquals(Product.objects.count(), initial_product_count + 1)
		self.assertEquals(ProductImage.objects.count(), initial_product_image_count + 1)
		self.assertRedirects(response, Product.get_list_url(), status_code=302, target_status_code=200)

	def test_post_request_invalid_data(self):
		"""Make sure an exception is raised if stock is 0 and product is set as ACTIVE"""
		self.client.login(username=self.superuser.username, password=self.password)
		initial_product_count = Product.objects.count()
		initial_product_image_count = ProductImage.objects.count()
		with open('static/images/for_testing/dummy_image1.jpg', 'rb') as file:
			form_data = {
				'name': 'valid p1',
				'price': 10,
				'status': Product.ACTIVE,
				'stock': 0,
				'image': file,
			}
			response = self.client.post(self.url, data=form_data)

		self.assertEquals(Product.objects.count(), initial_product_count)
		self.assertEquals(ProductImage.objects.count(), initial_product_image_count)
		self.assertFormError(ProductForm(form_data), 'status', [constants.PRODUCT_FORM_ERROR1])
		self.assertEquals(response.request.get('PATH_INFO'), self.url)
		self.assertEquals(response.status_code, 200)


class TestProductRead(ProductBaseTestCase):
	def setUp(self):
		super().setUp()
		self.active_product_url = self.active_product.get_read_url()
		self.inactive_product_url = self.inactive_product.get_read_url()
		self.superuser_cart = Cart.get_active_cart_or_create_new_cart(self.superuser)

	def test_user_access_active_product(self):
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(self.active_product_url)
		self.assertEquals(response.status_code, 200)

	def test_superuser_access_active_product(self):
		self.client.login(username=self.superuser.username, password=self.password)
		response = self.client.get(self.active_product_url)
		self.assertEquals(response.status_code, 200)

	def test_user_access_inactive_product(self):
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(self.inactive_product_url)
		self.assertEquals(response.status_code, 403)

	def test_superuser_access_inactive_product(self):
		self.client.login(username=self.superuser.username, password=self.password)
		response = self.client.get(self.inactive_product_url)
		self.assertEquals(response.status_code, 200)

	def test_get_request(self):
		self.client.login(username=self.superuser.username, password=self.password)
		response = self.client.get(self.active_product_url)
		context = response.context

		self.assertEquals(resolve(self.active_product_url).func, products.product_read)
		self.assertTemplateUsed(response, 'home/products/read.html')
		self.assertEquals(response.status_code, 200)

		self.assertIn('product', context)
		self.assertIn('form', context)

		self.assertEquals(context['product'], self.active_product)
		self.assertIsInstance(context['form'], QuantityForm)

	def test_post_request_valid_data(self):
		self.client.login(username=self.superuser.username, password=self.password)
		initial_cartitem_count = CartItem.objects.count()
		form_data = {
			'quantity': 5,
		}
		response = self.client.post(self.active_product_url, data=form_data)
		cartitems = self.superuser_cart.get_cartitems()

		self.assertEquals(CartItem.objects.count(), initial_cartitem_count + 1)
		self.assertEquals(cartitems.count(), 1)
		self.assertEquals(cartitems[0].quantity, 5)
		self.assertRedirects(response, self.superuser_cart.get_read_url(), status_code=302, target_status_code=200)

	def test_post_request_invalid_data(self):
		self.client.login(username=self.superuser.username, password=self.password)
		initial_cartitem_count = CartItem.objects.count()
		form_data = {
			'quantity': 0,
		}
		response = self.client.post(self.active_product_url, data=form_data)
		cartitems = self.superuser_cart.get_cartitems()

		self.assertEquals(CartItem.objects.count(), initial_cartitem_count)
		self.assertEquals(cartitems.count(), 0)
		self.assertEquals(response.request.get('PATH_INFO'), self.active_product_url)
		self.assertEquals(response.status_code, 200)


class TestProductUpdate(ProductBaseTestCase):
	def setUp(self):
		super().setUp()
		self.active_product_url = self.active_product.get_update_url()
		self.superuser_cart = Cart.get_active_cart_or_create_new_cart(self.superuser)

	def test_superuser_access(self):
		self.client.login(username=self.superuser.username, password=self.password)
		response = self.client.get(self.active_product_url)
		self.assertEquals(response.status_code, 200)

	def test_user_access(self):
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(self.active_product_url)
		self.assertEquals(response.status_code, 403)

	def test_get_request(self):
		self.client.login(username=self.superuser.username, password=self.password)
		response = self.client.get(self.active_product_url)
		context = response.context

		self.assertEquals(resolve(self.active_product_url).func, products.product_update)
		self.assertTemplateUsed(response, 'home/products/update.html')
		self.assertEquals(response.status_code, 200)

		self.assertIn('product', context)
		self.assertIn('product_form', context)
		self.assertIn('product_image_form', context)

		self.assertEquals(context['product'], self.active_product)
		self.assertIsInstance(context['product_form'], ProductForm)
		self.assertIsInstance(context['product_image_form'], ProductImageForm)

	def test_post_request_valid_data(self):
		self.client.login(username=self.superuser.username, password=self.password)
		initial_product_count = Product.objects.count()
		initial_product_image_count = ProductImage.objects.count()
		with open('static/images/for_testing/dummy_image1.jpg', 'rb') as file:
			form_data = {
				'name': 'valid p1',
				'price': 10,
				'status': Product.ACTIVE,
				'stock': 10,
				'image': file,
			}
			response = self.client.post(self.active_product_url, data=form_data)
		self.assertEquals(Product.objects.count(), initial_product_count)
		self.assertEquals(ProductImage.objects.count(), initial_product_image_count + 1)
		self.assertRedirects(response, Product.get_list_url(), status_code=302, target_status_code=200)

	def test_post_request_invalid_data_stock_and_status(self):
		"""Make sure an exception is raised if stock is 0 and product is set as ACTIVE"""
		self.client.login(username=self.superuser.username, password=self.password)
		test_product = Product.objects.create(
			name='test product',
			description='description1',
			price=10,
			status=Product.ACTIVE,
			stock=10,
			stripe_product_id='...',
			stripe_price_id='...',
			creator=self.superuser,
			updater=self.superuser,
		)
		self.assertTrue(self.active_product.is_active())
		form_data = {
			'name': test_product.name,
			'description': test_product.description,
			'price': test_product.price,
			'status': test_product.status,
			'stock': 0,
			'stripe_product_id': test_product.stripe_product_id,
			'stripe_price_id': test_product.stripe_price_id,
			'creator': test_product.creator,
			'updater': test_product.updater,
		}
		form = ProductForm(form_data, instance=test_product)
		self.assertFormError(form, 'status', [constants.PRODUCT_FORM_ERROR1])


class TestProductDelete(ProductBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = self.active_product.get_delete_url()

	def test_superuser_access(self):
		self.client.login(username=self.superuser.username, password=self.password)
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)

	def test_user_access(self):
		self.client.login(username=self.user1.username, password=self.password)
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 403)

	def test_get_request(self):
		self.client.login(username=self.superuser.username, password=self.password)
		response = self.client.get(self.url)
		context = response.context

		self.assertEquals(resolve(self.url).func, products.product_delete)
		self.assertTemplateUsed(response, 'home/products/delete.html')
		self.assertEquals(response.status_code, 200)
		self.assertIn('product', context)
		self.assertEquals(context['product'], self.active_product)

	def test_post_request(self):
		self.client.login(username=self.superuser.username, password=self.password)
		initial_count = Product.objects.count()
		response = self.client.post(self.url)
		self.assertEquals(Product.objects.count(), initial_count - 1)
		self.assertRedirects(response, Product.get_list_url(), status_code=302, target_status_code=200)