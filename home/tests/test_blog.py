from django.urls import resolve
from django.forms.fields import Field
from home.tests.base import BaseTestCase
from blog.models import Post
from blog.forms import PostForm
from blog import views
from senior_project.utils import combine_form_dicts


class BlogBaseTestCase(BaseTestCase):
	def setUp(self):
		super().setUp()
		self.active_blog1 = Post.objects.create(title="Post 1", preview_text="Preview text", content="Post content", status=Post.ACTIVE, creator=self.superuser, updater=self.superuser)
		self.active_blog2 = Post.objects.create(title="Post 2", preview_text="Preview text", content="Post content", status=Post.ACTIVE, creator=self.superuser, updater=self.superuser)
		self.inactive_blog = Post.objects.create(title="Post 3", preview_text="Preview text", content="Post content", status=Post.INACTIVE, creator=self.superuser, updater=self.superuser)


class TestBlogList(BlogBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = Post.get_list_url()

	def test_blog_list(self):
		response = self.client.get(self.url)
		context = response.context

		self.assertEquals(resolve(self.url).func, views.post_list)
		self.assertTemplateUsed(response, 'blog/list.html')
		self.assertEquals(response.status_code, 200)

		self.assertIn('posts', context)
		self.assertIn('post_model', context)

		self.assertEqual(len(context['posts']), 2)
		self.assertEqual(context['post_model'], Post)

		for post in context['posts']:
			self.assertEquals(post.status, Post.ACTIVE)


class TestBlogCreate(BlogBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = Post.get_create_url()

	def test_superuser_access(self):
		self.client.login(username=self.superuser.username, password=self.superuser_password)
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)

	def test_user_access(self):
		self.client.login(username=self.user1.username, password=self.user1_password)
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 403)

	def test_get_request(self):
		self.client.login(username=self.superuser.username, password=self.superuser_password)
		response = self.client.get(self.url)
		context = response.context

		self.assertEquals(resolve(self.url).func, views.post_create)
		self.assertTemplateUsed(response, 'blog/create.html')
		self.assertEquals(response.status_code, 200)

		self.assertIn('form', context)
		self.assertIn('post_model', context)

		self.assertIsInstance(context['form'], PostForm)
		self.assertEquals(context['post_model'], Post)

	def test_post_request_valid_data(self):
		self.client.login(username=self.superuser.username, password=self.superuser_password)
		form_data = {
			'title': 'Title',
			'preview_text': 'Preview text',
			'content': 'Content',
			'status': Post.ACTIVE
		}
		form_data = combine_form_dicts(self.superuser, form_data)
		initial_count = Post.objects.count()
		response = self.client.post(self.url, data=form_data)
		self.assertEquals(Post.objects.count(), initial_count + 1)
		self.assertRedirects(response, Post.get_list_url(), status_code=302, target_status_code=200)

	def test_post_request_invalid_data(self):
		form_data = {
			'title': 'Title',
			'preview_text': 'Preview text',
			# 'content': is required
		}
		form_data = combine_form_dicts(self.superuser, form_data)
		self.client.login(username=self.superuser.username, password=self.superuser_password)
		initial_count = Post.objects.count()
		response = self.client.post(self.url, data=form_data)
		self.assertEquals(initial_count, initial_count)  # data invalid, no post should've been created
		self.assertFormError(PostForm(form_data), 'content', [Field.default_error_messages['required']])
		self.assertEquals(response.request.get('PATH_INFO'), self.url)
		self.assertEquals(response.status_code, 200)


class TestBlogRead(BlogBaseTestCase):
	def setUp(self):
		super().setUp()
		self.active_blog_url = self.active_blog1.get_read_url()
		self.inactive_blog_url = self.inactive_blog.get_read_url()

	def test_read_active_post(self):
		response = self.client.get(self.active_blog_url)
		context = response.context

		self.assertEquals(resolve(self.active_blog_url).func, views.post_read)
		self.assertTemplateUsed(response, 'blog/read.html')
		self.assertEquals(response.status_code, 200)

		self.assertIn('post', context)
		self.assertIn('post_model', context)

		self.assertEquals(context['post'], self.active_blog1)
		self.assertEquals(context['post_model'], Post)
		self.assertEquals(context['post'].status, Post.ACTIVE)

	def test_inactive_post_superuser_access(self):
		self.client.login(username=self.superuser.username, password=self.superuser_password)
		response = self.client.get(self.inactive_blog_url)
		self.assertEquals(response.status_code, 200)

	def test_inactive_post_user_access(self):
		self.client.login(username=self.user1.username, password=self.user1_password)
		response = self.client.get(self.inactive_blog_url)
		self.assertEquals(response.status_code, 403)


class TestBlogUpdate(BlogBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = self.active_blog1.get_update_url()

	def test_superuser_access(self):
		self.client.login(username=self.superuser.username, password=self.superuser_password)
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)

	def test_user_access(self):
		self.client.login(username=self.user1.username, password=self.user1_password)
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 403)

	def test_get_request(self):
		self.client.login(username=self.superuser.username, password=self.superuser_password)
		response = self.client.get(self.url)
		context = response.context

		self.assertEquals(resolve(self.url).func, views.post_update)
		self.assertTemplateUsed(response, 'blog/update.html')
		self.assertEquals(response.status_code, 200)

		self.assertIn('post', context)
		self.assertIn('form', context)
		self.assertIn('post_model', context)

		self.assertIsInstance(context['post'], Post)
		self.assertIsInstance(context['form'], PostForm)
		self.assertEquals(context['post_model'], Post)

	def test_post_request_valid_data(self):
		self.client.login(username=self.superuser.username, password=self.superuser_password)
		form_data = {
			'title': 'Title',
			'preview_text': 'Preview text',
			'content': 'Content',
			'status': Post.ACTIVE
		}
		form_data = combine_form_dicts(self.superuser, form_data)
		initial_count = Post.objects.count()
		response = self.client.post(self.url, data=form_data)
		self.assertEquals(initial_count, initial_count)
		self.assertRedirects(response, self.active_blog1.get_read_url(), status_code=302, target_status_code=200)

	def test_post_request_invalid_data(self):
		form_data = {
			'title': 'Title',
			'preview_text': 'Preview text',
			# 'content': is required
		}
		form_data = combine_form_dicts(self.superuser, form_data)
		self.client.login(username=self.superuser.username, password=self.superuser_password)
		initial_count = Post.objects.count()
		response = self.client.post(self.url, data=form_data)
		self.assertEquals(initial_count, initial_count)  # data invalid, no post should've been created
		self.assertFormError(PostForm(form_data), 'content', [Field.default_error_messages['required']])
		self.assertEquals(response.request.get('PATH_INFO'), self.url)
		self.assertEquals(response.status_code, 200)


class TestBlogDelete(BlogBaseTestCase):
	def setUp(self):
		super().setUp()
		self.url = self.active_blog1.get_delete_url()

	def test_superuser_access(self):
		self.client.login(username=self.superuser.username, password=self.superuser_password)
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 200)

	def test_user_access(self):
		self.client.login(username=self.user1.username, password=self.user1_password)
		response = self.client.get(self.url)
		self.assertEquals(response.status_code, 403)

	def test_get_request(self):
		self.client.login(username=self.superuser.username, password=self.superuser_password)
		response = self.client.get(self.url)
		context = response.context

		self.assertEquals(resolve(self.url).func, views.post_delete)
		self.assertTemplateUsed(response, 'blog/delete.html')
		self.assertEquals(response.status_code, 200)

		self.assertIn('post', context)

		self.assertIsInstance(context['post'], Post)

	def test_post_request(self):
		self.client.login(username=self.superuser.username, password=self.superuser_password)
		initial_count = Post.objects.count()
		response = self.client.post(self.url)
		self.assertEquals(initial_count-1, Post.objects.count())
		self.assertRedirects(response, Post.get_list_url(), status_code=302, target_status_code=200)
