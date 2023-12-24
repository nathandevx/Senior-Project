from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import logout, get_user_model, authenticate, login
from allauth.account.views import LoginView
from senior_project.utils import login_required, get_dummy_user, logout_required, get_num_available_dummy_users
from home.models import Order, OrderHistory
from users.forms import DeleteUserForm

User = get_user_model()


# Customizing django-allauth LoginView
class CustomLoginView(LoginView):
    def get_context_data(self, **kwargs):
        context = super(CustomLoginView, self).get_context_data(**kwargs)
        context['num_available_admin_users'] = get_num_available_dummy_users('ADMIN')
        context['num_available_customer_users'] = get_num_available_dummy_users('CUSTOMER')
        return context


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


# Used on login page to login the user as an admin
@logout_required
def login_as_admin(request):
    user = get_dummy_user("ADMIN")
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    messages.info(request, f'You logged in as {user.username}. You may be logged out in an hour.')
    return redirect('home:home')


# Used on login page to login the user as a customer
@logout_required
def login_as_customer(request):
    user = get_dummy_user("CUSTOMER")
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)
    messages.info(request, f'You logged in as {user.username}. You may be logged out in an hour.')
    return redirect('home:home')
