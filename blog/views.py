from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from blog.forms import PostForm
from blog.models import Post


def post_list(request):
	if request.user.is_superuser:
		posts = Post.objects.all()
	else:
		posts = Post.objects.filter(status=Post.ACTIVE)
	return render(request, 'blog/list.html', {'posts': posts, 'post_model': Post})


def post_create(request):
	if not request.user.is_superuser:
		return HttpResponseForbidden()
	if request.method == 'POST':
		form = PostForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			post.creator = request.user
			post.updater = request.user
			post.save()

			messages.success(request, f'Successfully created post: {post.title}')
			return redirect(Post.get_list_url())
	else:
		form = PostForm()
	return render(request, 'blog/create.html', {'form': form, 'post_model': Post})


def post_read(request, pk):
	post = Post.objects.get(pk=pk)
	return render(request, 'blog/read.html', {'post': post, 'post_model': Post})


def post_update(request, pk):
	if not request.user.is_superuser:
		return HttpResponseForbidden()
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


def post_delete(request, pk):
	if not request.user.is_superuser:
		return HttpResponseForbidden()
	post = get_object_or_404(Post, pk=pk)
	if request.method == 'POST':
		post.delete()
		return redirect(post.get_list_url())
	else:
		return render(request, 'blog/delete.html', {'post': post})
