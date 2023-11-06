from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import logout, get_user_model
from senior_project.utils import login_required
from home.models import Order, OrderHistory
from users.forms import DeleteUserForm

User = get_user_model()


@login_required
def profile(request):
    return render(request, 'users/profile.html')


def delete_user(request):
    if request.user.is_superuser:
        return render(request, 'home/cant_delete_account.html')
    if request.user.is_anonymous or not request.user.is_authenticated:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = DeleteUserForm(request.POST)

        if form.is_valid():
            if request.POST["delete_checkbox"]:
                user = User.objects.get(username=request.user)
                if user is not None:
                    OrderHistory.create_order_history_objs(Order.get_users_orders(user))
                    user.delete()  # delete the user account.
                    logout(request)  # log them out.
                    messages.info(request, "Your account has been deleted.")
                    return redirect(reverse("home:home"))
                else:
                    messages.info(request, "There was an error.")
    else:
        form = DeleteUserForm()
    return render(request, 'users/delete_account.html', {'form': form})
