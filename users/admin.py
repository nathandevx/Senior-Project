from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.conf import settings
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialApp
from .models import User


admin.site.register(User, UserAdmin)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialToken)
admin.site.unregister(SocialApp)

if not settings.DEBUG:  # in production
	admin.site.unregister(Group)
	admin.site.unregister(EmailAddress)
