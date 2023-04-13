from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import logout, get_user_model

from users.forms import DeleteUser

User = get_user_model()


def profile(request):
    return render(request, 'users/profile.html')


def delete_user(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = DeleteUser(request.POST)

            if form.is_valid():
                if request.POST["delete_checkbox"]:
                    rem = User.objects.get(username=request.user)
                    if rem is not None:
                        rem.delete()
                        logout(request)
                        messages.info(request, "Your account has been deleted.")
                        return redirect(reverse("home:home"))
                    else:
                        messages.info(request, "There was an error.")
        else:
            form = DeleteUser()
            context = {'form': form}
            return render(request, 'users/delete_account.html', context)
    if request.user.is_anonymous:
        return HttpResponse(render(request, "error_pages/404.html"), status=404)
