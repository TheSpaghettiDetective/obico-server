from django.db import models
from allauth.account.models import EmailAddress
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser, UserManager as BaseUserManager
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _
import uuid
from django.utils import timezone
from django.conf import settings

from lib import cache

UNLIMITED_DH = 100000000    # A very big number to indicate this is unlimited DH

def dh_is_unlimited(dh):
    return dh >= UNLIMITED_DH


class Syndicate(models.Model):
    sites = models.ManyToManyField(Site, related_name='syndicates')
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.name}'


@receiver(post_save, sender=Site)
def add_site_to_default_syndicate(sender, instance, created, **kwargs):
    if created:
        try:
            syndicate = Syndicate.objects.order_by('id').first()
            if syndicate:
                syndicate.sites.add(instance)
        except Syndicate.DoesNotExist:
            pass

post_save.connect(add_site_to_default_syndicate, sender=Site)


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""

        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'))
    syndicate = models.ForeignKey(Syndicate, on_delete=models.CASCADE, default=1)
    username = models.CharField(max_length=150, blank=True, null=True)
    consented_at = models.DateTimeField(null=True, blank=True)
    last_active_at = models.DateTimeField(null=True, blank=True)
    is_pro = models.BooleanField(null=False, blank=False, default=True)
    dh_balance = models.FloatField(null=False, default=0)
    unsub_token = models.UUIDField(null=False, blank=False, unique=True, db_index=True, default=uuid.uuid4, editable=False)
    account_notification_by_email = models.BooleanField(null=False, blank=False, default=True)
    mobile_app_canary = models.BooleanField(null=False, blank=False, default=False)
    tunnel_cap_multiplier = models.FloatField(null=False, blank=False, default=1)
    notification_enabled = models.BooleanField(null=False, blank=False, default=True)
    unseen_printer_events = models.IntegerField(null=False, blank=False, default=0)

    class Meta:
        unique_together = [['email', 'syndicate']]

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    DEFAULT_SYNDICATE = Syndicate(name='base')

    objects = UserManager()

    def sms_eligible(self):
        return self.phone_number and self.phone_country_code

    @property
    def is_primary_email_verified(self):
        if EmailAddress.objects.filter(user=self, email=self.email, verified=True).exists():
            return True

        return False

    @property
    def is_dh_unlimited(self):
        return self.dh_balance >= UNLIMITED_DH

    def tunnel_cap(self):
        return -1 if self.is_pro else settings.OCTOPRINT_TUNNEL_CAP * self.tunnel_cap_multiplier

    def tunnel_usage_over_cap(self):
        if self.tunnel_cap() < 0:
            return False
        else:
            return cache.octoprinttunnel_get_stats(self.id) > self.tunnel_cap() * 1.1 # Cap x 1.1 to give some grace period to users


# We use a signal as opposed to a form field because users may sign up using social buttons
@receiver(post_save, sender=User)
def update_consented_at(sender, instance, created, **kwargs):
    if created:
        instance.consented_at = timezone.now()
        instance.save()