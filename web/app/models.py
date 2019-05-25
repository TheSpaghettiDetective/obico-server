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
from datetime import timedelta

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
    current_print = models.OneToOneField('Print', on_delete=models.SET_NULL, null=True, related_name='not_used')
    action_on_failure = models.CharField(
        max_length=10,
        choices=ACTION_ON_FAILURE,
        default=PAUSE,
    )
    tools_off_on_pause = models.BooleanField(default=True)
    bed_off_on_pause = models.BooleanField(default=False)
    retract_on_pause = models.FloatField(null=False, default=6.5)
    lift_z_on_pause = models.FloatField(null=False, default=2.5)
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

    def update_current_print(self, filename, current_print_ts):
        if current_print_ts == -1:      # Not printing
            if self.current_print:
                self.unset_current_print_with_ts()
        else:                           # currently printing
            if self.current_print:
                if self.current_print.ext_id != current_print_ts:
                    self.unset_current_print_with_ts()
                    self.set_current_print_with_ts(filename, current_print_ts)
            else:
                self.set_current_print_with_ts(filename, current_print_ts)

    def unset_current_print_with_ts(self):
        if self.current_print.cancelled_at is None:
            self.current_print.finished_at = timezone.now()
        self.current_print.save()
        self.current_print = None
        self.save()

        self.printerprediction.reset_for_new_print()

    def set_current_print_with_ts(self, filename, current_print_ts):
        if current_print_ts and current_print_ts != -1:
            cur_print, _ = Print.objects.get_or_create(
                printer=self,
                ext_id=current_print_ts,
                defaults={'filename': filename, 'started_at': timezone.now()},
                )
        else:
            cur_print = Print.objects.create(
                printer=self,
                filename=filename,
                started_at=timezone.now(),
                )
        self.current_print = cur_print
        self.save()

        self.printerprediction.reset_for_new_print()

    ####
    ## Backward compatibility. Old way of setting print without current_print_ts
    #####
    def set_current_print(self, filename):
        if self.current_print:
            if self.current_print.filename == filename:
                return
            else:
                self.unset_current_print_with_ts()

        self.set_current_print_with_ts(filename, None)

    def unset_current_print(self, cancelled):
        if self.current_print:  # was printing now it is not
            if cancelled:
                self.current_print.cancelled_at = timezone.now()

            self.unset_current_print_with_ts()

    ###### End of old way of setting/unsetting print

    def is_printing(self):
        return self.current_print != None

    def resume_print(self, mute_alert=False):
        self.acknowledge_alert()
        if mute_alert:
            self.mute_current_print(True)

        # TODO: find a more elegant way to prevent rage clicking
        last_commands = self.printercommand_set.order_by('-id')[:1]
        if len(last_commands) > 0 and last_commands[0].created_at > timezone.now() - timedelta(seconds=10):
            return

        self.queue_octoprint_command('resume')

    def pause_print(self):

        # TODO: find a more elegant way to prevent rage clicking
        last_commands = self.printercommand_set.order_by('-id')[:1]
        if len(last_commands) > 0 and last_commands[0].created_at > timezone.now() - timedelta(seconds=10):
            return

        args = {'retract': self.retract_on_pause, 'lift_z': self.lift_z_on_pause}
        if self.tools_off_on_pause:
            args['tools_off'] = True
        if self.bed_off_on_pause:
            args['bed_off'] = True
        self.queue_octoprint_command('pause', args=args)

    def cancel_print(self):
        self.acknowledge_alert()
        self.queue_octoprint_command('cancel')

    def set_alert(self):
        self.current_print.alerted_at = timezone.now()
        self.current_print.alert_acknowledged_at = None
        self.current_print.save()

    def acknowledge_alert(self):
        self.current_print.alerted_at = None
        self.current_print.alert_acknowledged_at = timezone.now()
        self.current_print.save()

    def mute_current_print(self, muted):
        self.current_print.alert_muted_at = timezone.now() if muted else None
        self.current_print.save()

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
    ext_id = models.IntegerField(null=True, blank=True)
    filename = models.CharField(max_length=1000, null=False, blank=False)
    started_at = models.DateTimeField(null=False, blank=False)
    finished_at = models.DateTimeField(null=True)
    cancelled_at = models.DateTimeField(null=True)
    alerted_at = models.DateTimeField(null=True)
    alert_acknowledged_at = models.DateTimeField(null=True)
    alert_muted_at = models.DateTimeField(null=True)
    video_url = models.CharField(max_length=2000, null=True)
    tagged_video_url = models.CharField(max_length=2000, null=True)
    poster_url = models.CharField(max_length=2000, null=True)
    prediction_json_url = models.CharField(max_length=2000, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    if os.environ.get('ENALBE_HISTORY', '') == 'True':
        history = HistoricalRecords()

    def ended_at(self):
        return self.cancelled_at or self.finished_at

    def end_status(self):
        return '(Cancelled)' if self.cancelled_at else ''

    def duration(self):
        return self.ended_at() - self.started_at
