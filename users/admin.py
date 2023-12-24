from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from .models import User


admin.site.register(User, UserAdmin)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialToken)
admin.site.unregister(SocialApp)
