from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from senior_project.utils import superuser_or_admin_required
from blog.forms import PostForm
from blog.models import Post


def post_list(request):
	posts = Post.get_active_posts()
	return render(request, 'blog/list.html', {'posts': posts, 'post_model': Post})


@superuser_or_admin_required
def post_create(request):
	if request.method == 'POST':
		form = PostForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			post.creator = request.user
			post.updater = request.user
			post.save()

			messages.success(request, f'Successfully created post: {post.title}')
			return redirect(post.get_read_url())
	else:
		form = PostForm()
	return render(request, 'blog/create.html', {'form': form, 'post_model': Post})


def post_read(request, pk):
	post = Post.objects.get(pk=pk)
	if not post.is_admin_or_active_post(request.user):
		return HttpResponseForbidden()
	return render(request, 'blog/read.html', {'post': post, 'post_model': Post})


@superuser_or_admin_required
def post_update(request, pk):
	post = get_object_or_404(Post, pk=pk)

	if request.method == 'POST':
		form = PostForm(request.POST, instance=post)
		if form.is_valid():
			updated_post = form.save(commit=False)
			updated_post.creator = post.creator
			updated_post.updater = request.user
			updated_post.save()
			messages.success(request, f'Successfully updated post: {updated_post.title}')
			return redirect(post.get_read_url())
	else:
		form = PostForm(instance=post)
	return render(request, 'blog/update.html', {'form': form, 'post': post, 'post_model': Post})


@superuser_or_admin_required
def post_delete(request, pk):
	post = get_object_or_404(Post, pk=pk)
	if request.method == 'POST':
		post.delete()
		return redirect(post.get_list_url())
	else:
		return render(request, 'blog/delete.html', {'post': post})
