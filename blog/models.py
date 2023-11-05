from django.shortcuts import reverse
from django.db import models
from ckeditor.fields import RichTextField
from home.models import TimestampCreatorMixin


class Post(TimestampCreatorMixin):
	"""
	title: the title of the blog post. The h1 tag.
	preview_text: the text display on the blog post list page.
	content: the content of the blog.
	status: the blog status.
		- INACTIVE: the blog is not viewable by anyone but the admin. It doesn't show up on the blog post list page.
		- ACTIVE: the blog is viewable by everyone.
	"""
	ACTIVE = 'Active'
	INACTIVE = 'Inactive'
	title = models.CharField(default='', max_length=100)
	preview_text = models.TextField(default='', max_length=500)
	content = RichTextField(default='')
	status = models.CharField(default=INACTIVE, max_length=50, choices=[(ACTIVE, ACTIVE), (INACTIVE, INACTIVE)])

	def __str__(self):
		return self.title

	@staticmethod
	def get_list_url():
		return reverse('blog:post-list')

	@staticmethod
	def get_create_url():
		return reverse('blog:post-create')

	def get_read_url(self):
		return reverse('blog:post-read', kwargs={'pk': self.pk})

	def get_update_url(self):
		return reverse('blog:post-update', kwargs={'pk': self.pk})

	def get_delete_url(self):
		return reverse('blog:post-delete', kwargs={'pk': self.pk})

	@classmethod
	def get_active_posts(cls):
		return cls.objects.filter(status=cls.ACTIVE)

	def is_superuser_or_active_post(self, user):
		return user.is_superuser or self.status == Post.ACTIVE

	class Meta:
		verbose_name = 'Post'
		verbose_name_plural = 'Posts'
