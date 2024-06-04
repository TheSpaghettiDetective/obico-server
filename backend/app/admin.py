import sys

from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

from config import settings
from . import models
from .models import User, Printer, NotificationSetting, Print, GCodeFolder, GCodeFile
from django.apps import apps
import inspect
from django.contrib.admin.sites import AlreadyRegistered
from django.db.models import Model
from notifications.plugins.email import EmailNotificationPlugin
from notifications.handlers import handler

def send_test_email(modeladmin, request, queryset):
    for u in queryset.all():
        user_ctx = handler.get_user_context(u)
        EmailNotificationPlugin().send_emails(
            user=user_ctx,
            subject='Test email - it worked!',
            mailing_list='test',
            template_path='email/test_email.html',
            ctx={},
            verified_only=False,
        )
    messages.success(request, 'Test email sent. Check your server logs if you do not see test email in your inbox.')


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password', 'syndicate')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'syndicate'),
        }),
    )
    
    ordering = ('email',)
    actions = [send_test_email]
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('syndicate',)
        return self.readonly_fields


class PrinterAdmin(admin.ModelAdmin):
    exclude = ('current_img_url', 'detection_score')

@admin.register(NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    list_select_related = True
    list_display = ('get_user', 'name', 'enabled', 'notify_on_failure_alert', 'notify_on_print_done',
        'notify_on_print_cancelled', 'notify_on_filament_change', 'notify_on_heater_status',
        'notify_on_print_start','notify_on_print_pause','notify_on_print_resume',)
    search_fields = ('user__email',)
    readonly_fields = ['user', ]

    def get_user(self, obj):
        return obj.user.email

@admin.register(Print)
class PrintAdmin(admin.ModelAdmin):
    exclude = [x for x in Print.__dict__.keys() if x.endswith('at')] + ['alert_overwrite']
