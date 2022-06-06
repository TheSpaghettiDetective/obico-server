from django.contrib import admin
from allauth.account.models import EmailAddress

# Register your models here.

admin.site.unregister(EmailAddress)
