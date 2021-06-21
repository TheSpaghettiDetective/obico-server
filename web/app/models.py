from typing import Dict, List, Optional
from allauth.account.admin import EmailAddress
from datetime import datetime, timedelta
import logging
import os
import json
from django.db import models, IntegrityError
from jsonfield import JSONField
import uuid
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from safedelete.models import SafeDeleteModel
from safedelete.managers import SafeDeleteManager
from pushbullet import Pushbullet, errors
from django.utils.html import mark_safe

from config.celery import celery_app
from lib import cache, channels
from lib.utils import dict_or_none

LOGGER = logging.getLogger(__name__)

UNLIMITED_DH = 100000000    # A very big number to indicate this is unlimited DH


class ResurrectionError(Exception):
    pass


def dh_is_unlimited(dh):
    return dh >= UNLIMITED_DH


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
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    phone_country_code = models.CharField(max_length=5, null=True, blank=True)
    pushbullet_access_token = models.CharField(max_length=45, null=True, blank=True)
    telegram_chat_id = models.BigIntegerField(null=True, blank=True)
    slack_access_token = models.CharField(max_length=128, null=True, blank=True)
    consented_at = models.DateTimeField(null=True, blank=True)
    is_pro = models.BooleanField(null=False, blank=False, default=True)
    dh_balance = models.FloatField(null=False, default=0)
    unsub_token = models.UUIDField(null=False, blank=False, unique=True, db_index=True, default=uuid.uuid4, editable=False)
    notify_on_done = models.BooleanField(null=False, blank=False, default=True)
    notify_on_canceled = models.BooleanField(null=False, blank=False, default=False)
    print_notification_by_email = models.BooleanField(null=False, blank=False, default=True)
    account_notification_by_email = models.BooleanField(null=False, blank=False, default=True)
    alert_by_email = models.BooleanField(null=False, blank=False, default=True)
    print_notification_by_pushbullet = models.BooleanField(null=False, blank=False, default=True)
    print_notification_by_telegram = models.BooleanField(null=False, blank=False, default=True)
    alert_by_sms = models.BooleanField(null=False, blank=False, default=True)
    discord_webhook = models.CharField(max_length=256, null=True, blank=True)
    print_notification_by_discord = models.BooleanField(null=False, blank=False, default=True)
    pushover_user_token = models.CharField(max_length=45, null=True, blank=True)
    print_notification_by_pushover = models.BooleanField(null=False, blank=False, default=True)
    mobile_app_canary = models.BooleanField(null=False, blank=False, default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

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

    def has_valid_pushbullet_token(self):
        if not self.pushbullet_access_token:
            return False

        try:
            Pushbullet(self.pushbullet_access_token)

            return True
        except errors.InvalidKeyError:
            return False

    def tunnel_usage_over_cap(self):
        return not self.is_pro and cache.octoprinttunnel_get_stats(self.id) > settings.OCTOPRINT_TUNNEL_CAP * 1.1  # Cap x 1.1 to give some grace period to users

# We use a signal as opposed to a form field because users may sign up using social buttons


@receiver(post_save, sender=User)
def update_consented_at(sender, instance, created, **kwargs):
    if created:
        instance.consented_at = timezone.now()
        instance.save()


class PrinterManager(SafeDeleteManager):
    def get_queryset(self):
        return super(PrinterManager, self).get_queryset().filter(archived_at__isnull=True)


class Printer(SafeDeleteModel):
    class Meta:
        default_manager_name = 'objects'

    PAUSE = 'PAUSE'
    NONE = 'NONE'
    ACTION_ON_FAILURE = (
        (NONE, 'Just notify me'),
        (PAUSE, 'Pause the printer and notify me'),
    )

    name = models.CharField(max_length=200, null=False)
    auth_token = models.CharField(max_length=28, unique=True, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    current_print = models.OneToOneField('Print', on_delete=models.SET_NULL, null=True, blank=True, related_name='not_used')
    action_on_failure = models.CharField(
        max_length=10,
        choices=ACTION_ON_FAILURE,
        default=PAUSE,
    )
    watching_enabled = models.BooleanField(default=True, db_column="watching")
    tools_off_on_pause = models.BooleanField(default=True)
    bed_off_on_pause = models.BooleanField(default=False)
    retract_on_pause = models.FloatField(null=False, default=6.5)
    lift_z_on_pause = models.FloatField(null=False, default=2.5)
    detective_sensitivity = models.FloatField(null=False, default=1.0)

    archived_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PrinterManager()
    with_archived = SafeDeleteManager()

    @property
    def status(self):
        return dict_or_none(cache.printer_status_get(self.id))

    @property
    def pic(self):
        pic_data = cache.printer_pic_get(self.id)

        return dict_or_none(pic_data)

    @property
    def settings(self):
        p_settings = cache.printer_settings_get(self.id)

        for key in ('webcam_flipV', 'webcam_flipH', 'webcam_rotate90'):
            p_settings[key] = p_settings.get(key, 'False') == 'True'
        p_settings['ratio169'] = p_settings.get('webcam_streamRatio', '4:3') == '16:9'

        if p_settings.get('temp_profiles'):
            p_settings['temp_profiles'] = json.loads(p_settings.get('temp_profiles'))

        return p_settings

    # should_watch and not_watching_reason follow slightly different rules
    # should_watch is used by the plugin. Therefore printing status is not a factor, otherwise we may have a feedback cycle:
    #    printer paused -> update server cache -> send should_watch to plugin -> udpate server
    # not_watching_reason is used by the web app and mobile app

    def should_watch(self):
        if not self.watching_enabled or self.user.dh_balance < 0:
            return False

        return self.current_print is not None and self.current_print.alert_muted_at is None

    def not_watching_reason(self):
        if not self.watching_enabled:
            return '"Watch for failures" is turned off'

        if self.user.dh_balance < 0:
            return "You have run out of Detective Hours"

        if not self.actively_printing():
            return "Printer is not actively printing"

        if self.current_print is not None and self.current_print.alert_muted_at is not None:
            return "Alerts are muted for current print"

        return None

    def actively_printing(self):
        printer_cur_state = cache.printer_status_get(self.id, 'state')

        return printer_cur_state and printer_cur_state.get('flags', {}).get('printing', False)

    def update_current_print(self, filename, current_print_ts):
        if current_print_ts == -1:      # Not printing
            if self.current_print:
                if self.current_print.started_at < (timezone.now() - timedelta(hours=10)):
                    self.unset_current_print()
                else:
                    LOGGER.warn(f'current_print_ts=-1 received when current print is still active. print_id: {self.current_print_id} - printer_id: {self.id}')

            return

        # currently printing

        if self.current_print:
            if self.current_print.ext_id == current_print_ts:
                return
            # Unknown bug in plugin that causes current_print_ts not unique

            if self.current_print.ext_id in range(current_print_ts - 20, current_print_ts + 20) and self.current_print.filename == filename:
                LOGGER.warn(
                    f'Apparently skewed print_ts received. ts1: {self.current_print.ext_id} - ts2: {current_print_ts} - print_id: {self.current_print_id} - printer_id: {self.id}')

                return
            LOGGER.warn(f'Print not properly ended before next start. Stale print_id: {self.current_print_id} - printer_id: {self.id}')
            self.unset_current_print()
            self.set_current_print(filename, current_print_ts)
        else:
            self.set_current_print(filename, current_print_ts)

    def unset_current_print(self):
        print = self.current_print
        self.current_print = None
        self.save()

        self.printerprediction.reset_for_new_print()

        if print.cancelled_at is None:
            print.finished_at = timezone.now()
            print.save()

        PrintEvent.create(print, PrintEvent.ENDED)
        self.send_should_watch_status()

    def set_current_print(self, filename, current_print_ts):
        if not current_print_ts or current_print_ts == -1:
            raise Exception(f'Invalid current_print_ts when trying to set current_print: {current_print_ts}')

        try:
            cur_print, _ = Print.objects.get_or_create(
                user=self.user,
                printer=self,
                ext_id=current_print_ts,
                defaults={'filename': filename.strip(), 'started_at': timezone.now()},
            )
        except IntegrityError:
            raise ResurrectionError('Current print is deleted! printer_id: {} | print_ts: {} | filename: {}'.format(self.id, current_print_ts, filename))

        if cur_print.ended_at():
            if cur_print.ended_at() > (timezone.now() - timedelta(seconds=30)):  # Race condition. Some msg with valid print_ts arrived after msg with print_ts=-1
                return
            else:
                raise ResurrectionError('Ended print is re-surrected! printer_id: {} | print_ts: {} | filename: {}'.format(self.id, current_print_ts, filename))

        self.current_print = cur_print
        self.save()

        self.printerprediction.reset_for_new_print()
        PrintEvent.create(cur_print, PrintEvent.STARTED)
        self.send_should_watch_status()

    ## return: succeeded? ##
    def resume_print(self, mute_alert=False):
        if self.current_print is None:  # when a link on an old email is clicked
            return False

        self.current_print.paused_at = None
        self.current_print.save()

        self.acknowledge_alert(Print.NOT_FAILED)
        self.send_octoprint_command('resume')

        return True

    ## return: succeeded? ##
    def pause_print(self):
        if self.current_print is None:
            return False

        self.current_print.paused_at = timezone.now()
        self.current_print.save()

        args = {'retract': self.retract_on_pause, 'lift_z': self.lift_z_on_pause}

        if self.tools_off_on_pause:
            args['tools_off'] = True

        if self.bed_off_on_pause:
            args['bed_off'] = True
        self.send_octoprint_command('pause', args=args)

        return True

    ## return: succeeded? ##
    def cancel_print(self):
        if self.current_print is None:  # when a link on an old email is clicked
            return False

        self.acknowledge_alert(Print.FAILED)
        self.send_octoprint_command('cancel')

        return True

    def set_alert(self):
        self.current_print.alerted_at = timezone.now()
        self.current_print.save()

    def acknowledge_alert(self, alert_overwrite):
        if not self.current_print.alerted_at:   # Not even alerted. Shouldn't be here. Maybe user error?
            return

        self.current_print.alert_acknowledged_at = timezone.now()
        self.current_print.alert_overwrite = alert_overwrite
        self.current_print.save()

    def mute_current_print(self, muted):
        self.current_print.alert_muted_at = timezone.now() if muted else None
        self.current_print.save()

        if muted:
            PrintEvent.create(self.current_print, PrintEvent.ALERT_MUTED)
        else:
            PrintEvent.create(self.current_print, PrintEvent.ALERT_UNMUTED)

        self.send_should_watch_status()

    # messages to printer

    def send_octoprint_command(self, command, args={}):
        channels.send_msg_to_printer(self.id, {'commands': [{'cmd': command, 'args': args}]})

    def send_should_watch_status(self, refresh=True):
        if refresh:
            self.refresh_from_db()
        channels.send_msg_to_printer(self.id, {'remote_status': {'should_watch': self.should_watch()}})

    def __str__(self):
        return str(self.id)


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


def calc_normalized_p(detective_sensitivity: float,
                      pred: 'PrinterPrediction') -> float:
    def scale(oldValue, oldMin, oldMax, newMin, newMax):
        newValue = (((oldValue - oldMin) * (newMax - newMin)) / (oldMax - oldMin)) + newMin
        return min(newMax, max(newMin, newValue))

    thresh_warning = (pred.rolling_mean_short - pred.rolling_mean_long) * settings.ROLLING_MEAN_SHORT_MULTIPLE
    thresh_warning = min(settings.THRESHOLD_HIGH, max(settings.THRESHOLD_LOW, thresh_warning))
    thresh_failure = thresh_warning * settings.ESCALATING_FACTOR

    p = (pred.ewm_mean - pred.rolling_mean_long) * detective_sensitivity

    if p > thresh_failure:
        return scale(p, thresh_failure, thresh_failure * 1.5, 2.0 / 3.0, 1.0)
    elif p > thresh_warning:
        return scale(p, thresh_warning, thresh_failure, 1.0 / 3.0, 2.0 / 3.0)
    else:
        return scale(p, 0, thresh_warning, 0, 1.0 / 3.0)


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
    p_json_url = models.CharField(max_length=2000, null=False, blank=False)
    creator_name = models.CharField(max_length=500, null=False, blank=False)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Print(SafeDeleteModel):

    class Meta:
        unique_together = [['printer', 'ext_id']]

    FAILED = 'FAILED'
    NOT_FAILED = 'NOT_FAILED'
    PARTIALY_FAILED = 'PARTIALY_FAILED'

    ALERT_OVERWRITE = (
        (FAILED, FAILED),
        (NOT_FAILED, NOT_FAILED),
        (PARTIALY_FAILED, PARTIALY_FAILED),
    )

    printer = models.ForeignKey(Printer, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    ext_id = models.IntegerField(null=True, blank=True)
    filename = models.CharField(max_length=1000, null=False, blank=False)
    started_at = models.DateTimeField(null=True)
    finished_at = models.DateTimeField(null=True)
    cancelled_at = models.DateTimeField(null=True)
    uploaded_at = models.DateTimeField(null=True)
    alerted_at = models.DateTimeField(null=True)
    alert_acknowledged_at = models.DateTimeField(null=True)
    alert_muted_at = models.DateTimeField(null=True)
    paused_at = models.DateTimeField(null=True)
    video_url = models.CharField(max_length=2000, null=True)
    tagged_video_url = models.CharField(max_length=2000, null=True)
    poster_url = models.CharField(max_length=2000, null=True)
    prediction_json_url = models.CharField(max_length=2000, db_index=True, null=True)
    alert_overwrite = models.CharField(
        max_length=20,
        choices=ALERT_OVERWRITE,
        null=True
    )
    access_consented_at = models.DateTimeField(null=True, blank=True)
    video_archived_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def ended_at(self):
        return self.cancelled_at or self.finished_at

    def duration(self):
        return self.ended_at() - self.started_at

    def has_alerted(self):
        return self.alerted_at

    def is_canceled(self):
        return bool(self.cancelled_at)

    @property
    def expecting_detective_view(self):
        return self.tagged_video_url or self.uploaded_at


class PrintEvent(models.Model):
    STARTED = 'STARTED'
    ENDED = 'ENDED'
    PAUSED = 'PAUSED'
    RESUMED = 'RESUMED'
    ALERT_MUTED = 'ALERT_MUTED'
    ALERT_UNMUTED = 'ALERT_UNMUTED'

    EVENT_TYPE = (
        (STARTED, STARTED),
        (ENDED, ENDED),
        (PAUSED, PAUSED),
        (RESUMED, RESUMED),
        (ALERT_MUTED, ALERT_MUTED),
        (ALERT_UNMUTED, ALERT_UNMUTED),
    )

    STOPPING_EVENT_TYPES = (ENDED, PAUSED, ALERT_MUTED)

    print = models.ForeignKey(Print, on_delete=models.CASCADE, null=False)
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE,
        null=True
    )
    alert_muted = models.BooleanField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def create(print, event_type):
        event = PrintEvent.objects.create(
            print=print,
            event_type=event_type,
            alert_muted=(print.alert_muted_at is not None)
        )

        if event_type in PrintEvent.ENDED:
            celery_app.send_task(settings.PRINT_EVENT_HANDLER, args=[print.id])


class SharedResource(models.Model):
    printer = models.OneToOneField(Printer, on_delete=models.CASCADE, null=True)
    share_token = models.CharField(max_length=40, unique=True, null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)


class GCodeFile(SafeDeleteModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    filename = models.CharField(max_length=1000, null=False, blank=False)
    safe_filename = models.CharField(max_length=1000, null=False, blank=False)
    url = models.CharField(max_length=2000, null=False, blank=False)
    num_bytes = models.BigIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PrintShotFeedback(models.Model):
    LOOKS_BAD = 'LOOKS_BAD'
    LOOKS_OK = 'LOOKS_OK'
    UNANSWERED = 'UNDECIDED'

    ANSWER_CHOICES = (
        (LOOKS_BAD, "It contains spaghetti"),
        (LOOKS_OK, "It does NOT contain spaghetti"),
        (UNANSWERED, "I'll decide later"),
    )

    print = models.ForeignKey(Print, on_delete=models.SET_NULL, blank=True, null=True)

    image_url = models.CharField(max_length=2000, null=False, blank=False)

    answer = models.CharField(max_length=16, choices=ANSWER_CHOICES, blank=True, null=True, db_index=True)
    answered_at = models.DateTimeField(null=True, blank=True, db_index=True)
    persisted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def image_tag(self):
        return mark_safe(f'<img src="{self.image_url}" width="150" height="150" />')

    image_tag.short_description = 'Image'


class ActiveMobileDeviceManager(models.Manager):
    def get_queryset(self):
        return super(ActiveMobileDeviceManager, self).get_queryset().filter(deactivated_at__isnull=True)


class MobileDevice(models.Model):

    class Meta:
        unique_together = [['user', 'device_token']]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    platform = models.CharField(max_length=16, null=False, blank=False)
    app_version = models.CharField(max_length=16, null=False, blank=False)
    device_token = models.CharField(max_length=256, null=False, blank=False)
    deactivated_at = models.DateTimeField(null=True, blank=True, db_index=True)
    preferred_timezone = models.CharField(max_length=32, null=True, blank=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ActiveMobileDeviceManager()
    with_inactive = models.Manager()


class OneTimeVerificationCodeManager(models.Manager):
    def get_queryset(self):
        return super(OneTimeVerificationCodeManager, self).get_queryset().filter(expired_at__gte=timezone.now())


def two_hours_later():
    return timezone.now() + timedelta(hours=2)


class OneTimeVerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False, null=False)
    printer = models.ForeignKey(Printer, on_delete=models.SET_NULL, blank=True, null=True)
    code = models.CharField(max_length=16, null=False, blank=False, db_index=True)
    expired_at = models.DateTimeField(null=False, blank=False, default=two_hours_later, db_index=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OneTimeVerificationCodeManager()
    with_expired = models.Manager()


class HeaterTracker(models.Model):
    class Meta:
        unique_together = ('printer', 'name')

    printer = models.ForeignKey(Printer, on_delete=models.CASCADE)
    name = models.CharField(max_length=16, blank=False)
    target = models.FloatField()
    reached = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PrintHeaterTarget(models.Model):
    class Meta:
        unique_together = ('print', 'name')

    print = models.ForeignKey(Print, on_delete=models.CASCADE)
    name = models.CharField(max_length=16, blank=False)
    target = models.FloatField()
    offset = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
