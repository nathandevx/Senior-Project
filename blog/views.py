from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden
from senior_project.utils import superuser_required
from blog.forms import PostForm
from blog.models import Post
from django.http import HttpResponse


def post_list(request):
	if request.user.is_superuser:
		posts = Post.objects.all()
	else:
		posts = Post.objects.filter(status=Post.ACTIVE)
	return render(request, 'blog/list.html', {'posts': posts, 'post_model': Post})


@superuser_required
def post_create(request):
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
	if not post.is_superuser_or_active_post(request.user):
		return HttpResponseForbidden()
	return render(request, 'blog/read.html', {'post': post, 'post_model': Post})


@superuser_required
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


@superuser_required
def post_delete(request, pk):
	post = get_object_or_404(Post, pk=pk)
	if request.method == 'POST':
		post.delete()
		return redirect(post.get_list_url())
	else:
		return render(request, 'blog/delete.html', {'post': post})

import csv

def export_user_counts_to_csv(request, year):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="user_counts_{year}.csv"'

    months, user_counts = User.get_user_counts_by_month_for_year(year)

    writer = csv.writer(response)
    writer.writerow(['Month', 'User Count'])

    for month, count in zip(months, user_counts):
        writer.writerow([month, count])

    return response

def export_years_with_users_to_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="years_with_users.csv"'

    years_with_users = User.get_years_with_users_signups()

    writer = csv.writer(response)
    writer.writerow(['Year'])

    for year in years_with_users:
        writer.writerow([year])

    return response

