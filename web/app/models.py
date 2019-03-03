from datetime import datetime
from django.db import models
from jsonfield import JSONField
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from simple_history.models import HistoricalRecords
from safedelete.models import SafeDeleteModel
import os
import json

from lib import redis
from lib.utils import dict_or_none

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
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    phone_country_code = models.CharField(max_length=5, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def sms_eligible(self):
        return self.phone_number and self.phone_country_code


class Printer(SafeDeleteModel):
    CANCEL = 'CANCEL'
    PAUSE = 'PAUSE'
    NONE = 'NONE'

    ACTION_ON_FAILURE = (
        (NONE, 'Just notify me via email and text.'),
        (PAUSE, 'Pause the print and notify me via email and text.'),
        (CANCEL, 'Cancel the print and notifiy me (not available during beta testing).'),
    )

    name = models.CharField(max_length=200, null=False)
    auth_token = models.CharField(max_length=28, unique=True, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    current_print_filename = models.CharField(max_length=1000, null=True, blank=True)
    current_print_started_at = models.DateTimeField(null=True)
    print_status_updated_at = models.DateTimeField(null=False, blank=False, auto_now_add=True)
    current_print_alerted_at = models.DateTimeField(null=True)
    alert_acknowledged_at = models.DateTimeField(null=True)
    action_on_failure = models.CharField(
        max_length=10,
        choices=ACTION_ON_FAILURE,
        default=PAUSE,
    )
    tools_off_on_pause = models.BooleanField(default=True)
    bed_off_on_pause = models.BooleanField(default=False)
    detective_sensitivity = models.FloatField(null=False, default=1.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    if os.environ.get('ENALBE_HISTORY', '') == 'True':
        history = HistoricalRecords()

    @property
    def status(self):
        status_data = redis.printer_status_get(self.id)
        if 'seconds_left' in status_data:
            status_data['seconds_left'] = int(status_data['seconds_left'])
        return dict_or_none(status_data)

    @property
    def pic(self):
        pic_data = redis.printer_pic_get(self.id)
        return dict_or_none(pic_data)

    def set_current_print(self, filename):
        if filename != self.current_print_filename:
            self.current_print_filename = filename
            self.current_print_started_at = timezone.now()
            self.print_status_updated_at = timezone.now()
            self.current_print_alerted_at = None
            self.alert_acknowledged_at = None
            self.save()

            self.printerprediction.reset_for_new_print()

    def unset_current_print(self, cancelled):
        if self.is_printing():  # was printing now it is not
            print = Print(
                printer=self,
                filename=self.current_print_filename,
                started_at=self.current_print_started_at,
                )
            if cancelled:
                print.cancelled_at = timezone.now()
            else:
                print.finished_at = timezone.now()
            print.save()

            from app.tasks import compile_timelapse  # can't put import at the top of the file to avoid circular dependency
            compile_timelapse.delay(print.id)

            self.current_print_filename = None
            self.current_print_started_at = None
            self.print_status_updated_at = timezone.now()
            self.current_print_alerted_at = None
            self.alert_acknowledged_at = None
            self.save()

            self.printerprediction.reset_for_new_print()


    def is_printing(self):
        return self.current_print_filename and self.current_print_started_at

    def resume_print(self, mute_alert=False):
        self.acknowledge_alert()
        if not mute_alert:
            self.current_print_alerted_at = None   # reset current_print_alerted_at so that further alerts won't be surpressed.
        self.save()

        self.queue_octoprint_command('restore_temps')
        self.queue_octoprint_command('resume', abort_existing=False)

    def pause_print(self):
        self.queue_octoprint_command('pause')

    def pause_print_on_failure(self):
        self.queue_octoprint_command('pause')
        if self.tools_off_on_pause:
            self.queue_octoprint_command('set_temps', args={'heater': 'tools', 'target': 0, 'save': True}, abort_existing=False)
        if self.bed_off_on_pause:
            self.queue_octoprint_command('set_temps', args={'heater': 'bed', 'target': 0, 'save': True}, abort_existing=False)

    def cancel_print(self):
        self.acknowledge_alert()
        self.queue_octoprint_command('cancel')

    def set_alert(self):
        self.current_print_alerted_at = timezone.now()
        self.alert_acknowledged_at = None
        self.save()

    def acknowledge_alert(self):
        self.alert_acknowledged_at = timezone.now()
        self.save()

    def queue_octoprint_command(self, command, args={}, abort_existing=True):
        if abort_existing:
            PrinterCommand.objects.filter(printer=self, status=PrinterCommand.PENDING).update(status=PrinterCommand.ABORTED)
        PrinterCommand.objects.create(printer=self, command=json.dumps({'cmd': command, 'args': args}), status=PrinterCommand.PENDING)

    def __str__(self):
        return self.name


class PrinterCommand(models.Model):
    PENDING = 'PENDING'
    SENT = 'SENT'
    ABORTED = 'ABORTED'

    COMMAND_STATUSES = (
        (PENDING, 'pending'),
        (SENT, 'sent'),
        (ABORTED, 'aborted'),
    )

    printer = models.ForeignKey(Printer, on_delete=models.CASCADE, null=False)
    command = models.CharField(max_length=2000, null=False, blank=False)
    status = models.CharField(
        max_length=10,
        choices=COMMAND_STATUSES,
        default=PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PrinterPrediction(models.Model):
    printer = models.OneToOneField(Printer, on_delete=models.CASCADE, primary_key=True)
    current_frame_num = models.IntegerField(null=False, default=0)
    lifetime_frame_num = models.IntegerField(null=False, default=0)
    current_p = models.FloatField(null=False, default=0.0)
    ewm_mean = models.FloatField(null=False, default=0.0)
    rolling_mean_long = models.FloatField(null=False, default=0.0)
    rolling_mean_short = models.FloatField(null=False, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def reset_for_new_print(self):
        self.current_frame_num = 0
        self.current_p = 0.0
        self.ewm_mean = 0.0
        self.rolling_mean_short = 0.0
        self.save()

    def __str__(self):
        return '| printer_id: {} | current_p: {:.4f} | ewm_mean: {:.4f} | rolling_mean_short: {:.4f} | rolling_mean_long: {:.4f} | current_frame_num: {} | lifetime_frame_num: {} |'.format(
            self.printer_id,
            self.current_p,
            self.ewm_mean,
            self.rolling_mean_short,
            self.rolling_mean_long,
            self.current_frame_num,
            self.lifetime_frame_num,
        )

@receiver(post_save, sender=Printer)
def create_printer_prediction(sender, instance, created, **kwargs):
    if created:
        PrinterPrediction.objects.create(printer=instance)


class PublicTimelapse(models.Model):
    title = models.CharField(max_length=500)
    priority = models.IntegerField(null=False, default=1000000)
    video_url = models.CharField(max_length=2000, null=False, blank=False)
    poster_url = models.CharField(max_length=2000, null=False, blank=False)
    creator_name = models.CharField(max_length=500, null=False, blank=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    frame_p = JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Print(SafeDeleteModel):
    printer = models.ForeignKey(Printer, on_delete=models.CASCADE, null=False)
    filename = models.CharField(max_length=1000, null=False, blank=False)
    started_at = models.DateTimeField(null=False, blank=False)
    finished_at = models.DateTimeField(null=True)
    cancelled_at = models.DateTimeField(null=True)
    video_url = models.CharField(max_length=2000, null=True)
    tagged_video_url = models.CharField(max_length=2000, null=True)
    poster_url = models.CharField(max_length=2000, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
