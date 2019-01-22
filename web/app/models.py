from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import ugettext_lazy as _

from lib import redis

class UserManager(UserManager):
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
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class Printer(models.Model):
    name = models.CharField(max_length=200, null=False)
    auth_token = models.CharField(max_length=28, unique=True, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    @property
    def status(self):
        return redis.printer_status_get(self.id)

    @property
    def pic(self):
        pic_data = redis.printer_pic_get(self.id)
        if pic_data['score']:
            pic_data['score'] = float(pic_data['score'])
        return pic_data

    def __str__(self):
        return self.name