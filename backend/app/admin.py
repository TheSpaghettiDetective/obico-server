from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages

from .models import User, Printer, NotificationSetting
from lib.notifications import send_email


def send_test_email(modeladmin, request, queryset):
    for u in queryset.all():
        send_email(
            user=u,
            subject='Test email - it worked!',
            mailing_list='test',
            template_path='email/test_email.html',
            ctx={},
        )
    messages.success(request, 'Test email sent. Check your server logs if you do not see test email in your inbox.')


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    ordering = ('email',)
    actions = [send_test_email]


@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    exclude = ('current_img_url', 'detection_score')

@admin.register(NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    list_select_related = True
    list_display = ('get_user', 'name', 'enabled', 'notify_on_failure_alert', 'notify_on_print_done',
        'notify_on_print_cancelled', 'notify_on_filament_change', 'notify_on_other_print_events', 'notify_on_heater_status')
    search_fields = ('user__email',)
    readonly_fields = ['user', ]

    def get_user(self, obj):
        return obj.user.email
