from typing import Dict
from datetime import datetime, timedelta
import logging
import os
import json
from secrets import token_hex
from django.db import models, IntegrityError
from jsonfield import JSONField
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from safedelete.models import SafeDeleteModel
from safedelete.managers import SafeDeleteManager
from pushbullet import Pushbullet, errors
from django.utils.html import mark_safe
from django.contrib.auth.hashers import make_password
from django.db.models import F, Q
from django.db.models.constraints import UniqueConstraint
from django.contrib.sites.models import Site

from config.celery import celery_app
from lib import cache, channels
from lib.utils import dict_or_none, get_rotated_pic_url
from .syndicate_models import Syndicate, User

LOGGER = logging.getLogger(__name__)


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
    DEFAULT_WEBCAM_SETTINGS = {
        'name': '',
        'is_primary_camera': True,
        'flipV': False,
        'flipH': False,
        'rotation': 0,
        'streamRatio': '16:9',
    }

    name = models.CharField(max_length=256, null=False)
    auth_token = models.CharField(max_length=256, unique=True, null=False, blank=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    current_print = models.OneToOneField('Print', on_delete=models.SET_NULL, null=True, blank=True, related_name='not_used')
    action_on_failure = models.CharField(
        max_length=256,
        choices=ACTION_ON_FAILURE,
        default=PAUSE,
    )
    watching_enabled = models.BooleanField(default=True, db_column="watching")
    tools_off_on_pause = models.BooleanField(default=True)
    bed_off_on_pause = models.BooleanField(default=False)
    retract_on_pause = models.FloatField(null=False, default=6.5)
    lift_z_on_pause = models.FloatField(null=False, default=2.5)
    detective_sensitivity = models.FloatField(null=False, default=1.0)
    detection_bending_factor = models.FloatField(null=True, blank=True)
    min_timelapse_secs_on_finish = models.IntegerField(null=False, default=60*10)  # Default to 10 minutes. -1: timelapse disabled
    min_timelapse_secs_on_cancel = models.IntegerField(null=False, default=60*5)  # Default to 5 minutes. -1: timelapse disabled
    agent_name = models.CharField(max_length=64, null=True, blank=True)
    agent_version = models.CharField(max_length=64, null=True, blank=True)

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

        webcam_settings = self.DEFAULT_WEBCAM_SETTINGS.copy()

        if p_settings.get('webcams') is not None:
            p_settings['webcams'] = json.loads(p_settings.get('webcams'))

            ## Backward compatibility with mobile app 2.5 or earlier

            if len(p_settings['webcams']) > 0:
                webcam_settings = p_settings['webcams'][0]

        for key in ('flipV', 'flipH', 'rotate90', 'rotation', 'streamRatio'):
            p_settings['webcam_' + key] = webcam_settings.get(key)

        if 'webcam_rotation' in p_settings:
            rotation_int = int(p_settings['webcam_rotation'])
            p_settings['webcam_rotation'] = rotation_int if rotation_int in [0, 90, 180, 270] else 0
            p_settings['webcam_rotate90'] = rotation_int == 270 # backward compatibility with old mobile app
        elif 'webcam_rotate90' in p_settings: # Backward compatibility with old plugins
            p_settings['webcam_rotation'] = int(270 if p_settings['webcam_rotate90'] else 0)

        p_settings['ratio169'] = p_settings.get('webcam_streamRatio', '16:9') == '16:9'

        ## End of backward compatibility with mobile app 2.5 or earlier

        if p_settings.get('temp_profiles'):
            p_settings['temp_profiles'] = json.loads(p_settings.get('temp_profiles'))

        # Backward compatibility: for mobile app 2.8 or earlier
        if self.agent_name and self.agent_version:
            p_settings.update(dict(agent_name=self.agent_name, agent_version=self.agent_version))

        return p_settings

    # should_watch and not_watching_reason follow slightly different rules
    # should_watch is used by the plugin. Therefore printing status is not a factor, otherwise we may have a feedback cycle:
    #    printer paused -> update server cache -> send should_watch to plugin -> update server
    # not_watching_reason is used by the web app and mobile app

    def should_watch(self):
        if not self.watching_enabled or self.user.dh_balance < 0:
            return False

        return self.current_print is not None and self.current_print.alert_muted_at is None

    def not_watching_reason(self):
        if not self.watching_enabled:
            return 'AI failure detection is disabled'

        if self.user.dh_balance < 0:
            return "You have run out of AI Detection Hours"

        if not self.actively_printing():
            return "Printer is not actively printing"

        if self.current_print is not None and self.current_print.alert_muted_at is not None:
            return "Alerts are muted for current print"

        return None

    def actively_printing(self):
        printer_cur_state = cache.printer_status_get(self.id, 'state')

        return printer_cur_state and printer_cur_state.get('flags', {}).get('printing', False)

    def update_current_print(self, current_print_ts, g_code_file_id, filename):
        # current_print_ts == -1 => Not printing in OctoPrint or Moonraker
        if current_print_ts == -1:
            if self.current_print:
                LOGGER.warn(f'current_print_ts=-1 received when current print is still active. Force-closing print. print_id: {self.current_print_id} - printer_id: {self.id}')
                self.unset_current_print()
            return

        # current_print_ts != -1 => Currently printing in OctoPrint or Moonraker

        if not self.current_print:
            if filename:
                self.set_current_print(filename, g_code_file_id, current_print_ts)
            else:
                # Sometimes moonraker-obico sends current_print_ts without octoprint_data, which is a bug.
                LOGGER.warn(f'Active current_print_ts but filename is None in the status. current_print_ts: {current_print_ts} - printer_id: {self.id}')
            return

        if self.current_print.g_code_file_id != g_code_file_id:
            self.current_print.g_code_file_id = g_code_file_id
            self.current_print.save()

        # Current print in OctoPrint matches current_print in db. Nothing to update.
        if self.current_print.ext_id == current_print_ts:
            return

        # Unknown bug in plugin that causes current_print_ts to change by a few seconds. Suspected to be caused by two PrintStarted OctoPrint events in quick secession.
        # So we assume it's the same printer if 2 current_print_ts are within range, and filenames are the same
        if self.current_print.ext_id in range(current_print_ts - 20, current_print_ts + 20) and self.current_print.filename == filename:
            LOGGER.warn(
                f'Apparently skewed print_ts received. ts1: {self.current_print.ext_id} - ts2: {current_print_ts} - print_id: {self.current_print_id} - printer_id: {self.id}')
            self.current_print.ext_id = current_print_ts
            self.current_print.save()
        else:
            LOGGER.warn(f'Print not properly ended before next start. Stale print_id: {self.current_print_id} - printer_id: {self.id}')
            self.unset_current_print()
            self.set_current_print(filename, g_code_file_id, current_print_ts)


    def unset_current_print(self):
        print = self.current_print
        self.current_print = None
        self.save()

        self.printerprediction.reset_for_new_print()

        if print.cancelled_at is None:
            print.finished_at = timezone.now()
            print.save()

        PrinterEvent.create(print=print, event_type=PrinterEvent.ENDED, task_handler=True)
        self.send_should_watch_status()

    def set_current_print(self, filename, g_code_file_id, current_print_ts):
        filename = filename.strip()
        try:
            cur_print, _ = Print.objects.get_or_create(
                user=self.user,
                printer=self,
                ext_id=current_print_ts,
                defaults={'filename': filename, 'g_code_file_id': g_code_file_id, 'started_at': timezone.now()},
            )
        except IntegrityError:
            raise Exception('Current print is deleted! printer_id: {} | print_ts: {} | filename: {}'.format(self.id, current_print_ts, filename))

        if cur_print.ended_at():
            if cur_print.ended_at() > (timezone.now() - timedelta(seconds=30)):  # Race condition. Some msg with valid print_ts arrived after msg with print_ts=-1
                return
            else:
                raise Exception('Ended print is re-surrected! printer_id: {} | print_ts: {} | filename: {}'.format(self.id, current_print_ts, filename))

        self.current_print = cur_print
        self.save()

        self.printerprediction.reset_for_new_print()
        PrinterEvent.create(print=cur_print, event_type=PrinterEvent.STARTED, task_handler=True)
        self.send_should_watch_status()

    ## return: succeeded? ##
    def resume_print(self, mute_alert=False, initiator=None):
        if self.current_print is None:  # when a link on an old email is clicked
            return False
        self.current_print.alert_acknowledged(Print.NOT_FAILED)

        self.send_octoprint_command('resume', initiator=initiator)
        return True

    ## return: succeeded? ##
    def pause_print(self, initiator=None):
        if self.current_print is None:
            return False

        args = {'retract': self.retract_on_pause, 'lift_z': self.lift_z_on_pause}

        if self.tools_off_on_pause:
            args['tools_off'] = True

        if self.bed_off_on_pause:
            args['bed_off'] = True
        self.send_octoprint_command('pause', args=args, initiator=initiator)

        return True

    ## return: succeeded? ##
    def cancel_print(self, initiator=None):
        if self.current_print is None:  # when a link on an old email is clicked
            return False
        self.current_print.alert_acknowledged(Print.FAILED)
        self.send_octoprint_command('cancel', initiator=initiator)

        return True

    def set_alert(self):
        self.current_print.alerted_at = timezone.now()
        self.current_print.save()

    def mute_current_print(self, muted):
        self.current_print.alert_muted_at = timezone.now() if muted else None
        self.current_print.save()

        if muted:
            PrinterEvent.create(print=self.current_print, event_type=PrinterEvent.ALERT_MUTED, task_handler=True)
        else:
            PrinterEvent.create(print=self.current_print, event_type=PrinterEvent.ALERT_UNMUTED, task_handler=True)

        self.send_should_watch_status()

    # messages to printer

    def send_octoprint_command(self, command, args={}, initiator=None):
        channels.send_msg_to_printer(self.id, {'commands': [{'cmd': command, 'args': args, 'initiator': initiator or 'unknown'}]})

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
        max_length=256,
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


class Print(SafeDeleteModel):

    class Meta:
        unique_together = [['printer', 'ext_id']]

    FAILED = 'FAILED'
    NOT_FAILED = 'NOT_FAILED'

    ALERT_OVERWRITE = (
        (FAILED, FAILED),
        (NOT_FAILED, NOT_FAILED),
    )

    printer = models.ForeignKey(Printer, on_delete=models.CASCADE, null=True)
    g_code_file = models.ForeignKey('GCodeFile', on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    ext_id = models.IntegerField(null=True, blank=True)
    filename = models.CharField(max_length=1000, null=False, blank=False)
    started_at = models.DateTimeField(null=True, db_index=True)
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
        max_length=256,
        choices=ALERT_OVERWRITE,
        null=True
    )
    access_consented_at = models.DateTimeField(null=True, blank=True)
    video_archived_at = models.DateTimeField(null=True, blank=True, db_index=True)
    filament_used = models.FloatField(null=True)
    print_time = models.FloatField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def cancelled(self):
        self.cancelled_at = timezone.now()
        self.save()

    def alert_acknowledged(self, alert_overwrite):
        if not self.alerted_at:   # Not even alerted. Shouldn't be here. Maybe user error?
            return

        self.alert_acknowledged_at = timezone.now()
        self.alert_overwrite = alert_overwrite
        self.save()

    def ended_at(self):
        return self.cancelled_at or self.finished_at

    def duration(self):
        return self.ended_at() - self.started_at

    def has_alerted(self):
        return self.alerted_at

    def is_canceled(self):
        return bool(self.cancelled_at)

    def need_alert_overwrite(self):
        return self.alert_overwrite is None and self.tagged_video_url is not None

    def need_print_shot_feedback(self):
        # Calling .all() instead of .filter() avoids n+1 queries here
        return None in [feedback.answered_at for feedback in self.printshotfeedback_set.all()]

    @property
    def expecting_detective_view(self):
        return self.tagged_video_url or self.uploaded_at


class PrinterEvent(models.Model):

    STARTED = 'STARTED'
    ENDED = 'ENDED'
    PAUSED = 'PAUSED'
    RESUMED = 'RESUMED'
    FAILURE_ALERTED = 'FAILURE_ALERTED'
    ALERT_MUTED = 'ALERT_MUTED'
    ALERT_UNMUTED = 'ALERT_UNMUTED'
    FILAMENT_CHANGE = 'FILAMENT_CHANGE'
    PRINTER_ERROR = 'PRINTER_ERROR'

    EVENT_TYPE = (
        (STARTED, STARTED),
        (ENDED, ENDED),
        (PAUSED, PAUSED),
        (RESUMED, RESUMED),
        (FAILURE_ALERTED, FAILURE_ALERTED),
        (ALERT_MUTED, ALERT_MUTED),
        (ALERT_UNMUTED, ALERT_UNMUTED),
        (FILAMENT_CHANGE, FILAMENT_CHANGE),
        (PRINTER_ERROR, PRINTER_ERROR),
    )

    ERROR = 'ERROR'
    WARNING = 'WARNING'
    SUCCESS = 'SUCCESS'
    INFO = 'INFO'

    EVENT_CLASS = (
        (ERROR, ERROR),
        (WARNING, WARNING),
        (SUCCESS, SUCCESS),
        (INFO, INFO),
    )

    print = models.ForeignKey(Print, on_delete=models.CASCADE, null=True)
    printer = models.ForeignKey(Printer, on_delete=models.CASCADE, null=False)
    event_type = models.CharField(
        max_length=256,
        choices=EVENT_TYPE,
        null=False,
        db_index=True,
    )
    event_class = models.CharField(
        max_length=256,
        choices=EVENT_CLASS,
        null=False,
        db_index=True,
    )
    event_title = models.TextField(
        null=True,
        blank=True,
    )
    event_text = models.TextField(
        null=True,
        blank=True,
    )
    image_url = models.TextField(
        null=True,
        blank=True,
    )
    info_url = models.TextField(
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def create(task_handler=False, **kwargs):

        def printer_event_attrs_from_print(event_type, print_):
            if event_type == PrinterEvent.ENDED:
                if print_.is_canceled():
                    attrs = dict(event_class=PrinterEvent.WARNING, event_title='Print Job Canceled')
                else:
                    attrs = dict(event_class=PrinterEvent.SUCCESS, event_title='Print Job Finished')
            elif event_type == PrinterEvent.FAILURE_ALERTED:
                attrs = dict(event_class=PrinterEvent.ERROR, event_title='Possible Failure Detected')
            elif event_type == PrinterEvent.ALERT_MUTED:
                attrs = dict(event_class=PrinterEvent.WARNING, event_title='Watching Turned Off')
            elif event_type == PrinterEvent.FILAMENT_CHANGE:
                attrs = dict(event_class=PrinterEvent.WARNING, event_title='Filament Change Required')
            else:
                attrs = dict(event_class=PrinterEvent.INFO, event_title='Print Job ' + event_type.capitalize())

            attrs.update(dict(
                event_text=f'<div><i>Printer:</i> {print_.printer.name}</div><div><i>G-Code:</i> {print_.filename}</div>',
            ))
            return attrs

        # When PrinterEvent is associated with a specific print, more data can be populated.
        if kwargs.get('print') is not None:
            kwargs['printer'] = kwargs.get('print').printer

            is_print_job_event = kwargs.get('event_type') in (
                PrinterEvent.STARTED,
                PrinterEvent.ENDED,
                PrinterEvent.PAUSED,
                PrinterEvent.RESUMED,
                PrinterEvent.FAILURE_ALERTED,
                PrinterEvent.ALERT_MUTED,
                PrinterEvent.FILAMENT_CHANGE,
            )

            if is_print_job_event and kwargs.get('event_title') is None and kwargs.get('event_class') is None:
                attrs = printer_event_attrs_from_print(kwargs.get('event_type'), kwargs.get('print'))
                kwargs.update(attrs)

            if kwargs.get('image_url') is None:
                kwargs.update({'image_url': get_rotated_pic_url(kwargs.get('print').printer, force_snapshot=True)})

        printer_event = PrinterEvent.objects.create(**kwargs)

        printer_event.printer.user.unseen_printer_events += 1
        printer_event.printer.user.save()

        if task_handler:
            celery_app.send_task(
                settings.PRINT_EVENT_HANDLER,
                args=(printer_event.id, ),
            )


class SharedResource(models.Model):
    printer = models.OneToOneField(Printer, on_delete=models.CASCADE, null=True)
    share_token = models.CharField(max_length=256, unique=True, null=False, blank=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)


class GCodeFolder(models.Model):

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'parent_folder', 'safe_name'],
                             name='unique_with_parent_folder'),
            UniqueConstraint(fields=['user', 'safe_name'],
                             condition=Q(parent_folder=None),
                             name='unique_without_parent_folder'),
        ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    parent_folder = models.ForeignKey('GCodeFolder', on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=1000, null=False, blank=False)
    safe_name = models.CharField(max_length=1000, null=False, blank=False, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def g_code_folder_count(self):
        return self.gcodefolder_set.count()

    def g_code_file_count(self):
        return self.gcodefile_set.count()


class GCodeFile(SafeDeleteModel):
    class Meta:
        indexes = [
            models.Index(fields=['agent_signature'])
        ]
        # TODO: we will need to come back to turn on the unique constraints once we combine the same file names to versions
        # constraints = [
        #     UniqueConstraint(fields=['user', 'parent_folder', 'safe_filename'],
        #                      name='unique_with_parent_folder'),
        #     UniqueConstraint(fields=['user', 'safe_filename'],
        #                      condition=Q(parent_folder=None),
        #                      name='unique_without_parent_folder'),
        # ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    filename = models.CharField(max_length=1000, null=False, blank=False)
    safe_filename = models.CharField(max_length=1000, null=False, blank=False, db_index=True)
    parent_folder = models.ForeignKey(GCodeFolder, on_delete=models.CASCADE, null=True)
    url = models.CharField(max_length=2000, null=True, blank=False)
    num_bytes = models.BigIntegerField(null=True, blank=True, db_index=True)
    resident_printer = models.ForeignKey(Printer, on_delete=models.CASCADE, null=True)  # null for gcode files on the server
    # A value the agent can independently derive to match with the server. Format: scheme:value
    agent_signature = models.CharField(max_length=256, null=True, blank=False)
    metadata_json = models.TextField(null=True, blank=False)
    filament_total = models.FloatField(null=True)
    estimated_time = models.FloatField(null=True)
    thumbnail1_url = models.CharField(max_length=2000, null=True, blank=False)
    thumbnail2_url = models.CharField(max_length=2000, null=True, blank=False)
    thumbnail3_url = models.CharField(max_length=2000, null=True, blank=False)

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

    answer = models.CharField(max_length=256, choices=ANSWER_CHOICES, blank=True, null=True, db_index=True)
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
    platform = models.CharField(max_length=256, null=False, blank=False)
    app_version = models.CharField(max_length=256, null=False, blank=False)
    device_token = models.CharField(max_length=256, null=False, blank=False)
    deactivated_at = models.DateTimeField(null=True, blank=True, db_index=True)
    preferred_timezone = models.CharField(max_length=256, null=True, blank=False)

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
    code = models.CharField(max_length=256, null=False, blank=False, db_index=True)
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
    name = models.CharField(max_length=256, blank=False)
    target = models.FloatField()
    reached = models.BooleanField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PrintHeaterTarget(models.Model):
    class Meta:
        unique_together = ('print', 'name')

    print = models.ForeignKey(Print, on_delete=models.CASCADE)
    name = models.CharField(max_length=256, blank=False)
    target = models.FloatField()
    offset = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class OctoPrintTunnelManager(SafeDeleteManager):
    def get_queryset(self):
        return super(OctoPrintTunnelManager, self).get_queryset().filter(
            printer__user__is_active=True,
            printer__deleted__isnull=True,
            printer__archived_at__isnull=True)


class OctoPrintTunnel(SafeDeleteModel):
    # For INTERNAL_APP (TSD), tunnel is accessed by session cookie; Otherwise, it's by http basic auth
    INTERNAL_APP = 'Obico'

    printer = models.ForeignKey(Printer, on_delete=models.CASCADE, null=False)
    app = models.TextField(null=False, blank=False, db_index=True)

    basicauth_username = models.TextField(blank=True, null=True)
    basicauth_password = models.TextField(blank=True, null=True)

    # when tunnel is accessed by subdomain.
    subdomain_code = models.TextField(unique=True, blank=True, null=True, db_index=True)

    # when tunnel is accessed by port.
    port = models.IntegerField(null=True, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OctoPrintTunnelManager()

    @classmethod
    def get_or_create_for_internal_use(cls, printer) -> 'OctoPrintTunnel':
        pt = OctoPrintTunnel.objects.filter(
            printer=printer,
            app=cls.INTERNAL_APP,
        ).first()

        if pt is not None:
            return pt

        return cls.create(printer, app=cls.INTERNAL_APP)

    @classmethod
    def create(
        cls, printer: Printer, app: str
    ) -> 'OctoPrintTunnel':

        internal = app == cls.INTERNAL_APP
        if internal:
            instance = OctoPrintTunnel(
                printer=printer,
                basicauth_username=None,
                basicauth_password=None,
                app=app,
            )
        else:
            plain_basicauth_password = token_hex(32)
            basicauth_password = make_password(plain_basicauth_password)
            instance = OctoPrintTunnel(
                printer=printer,
                basicauth_username=token_hex(32),
                basicauth_password=basicauth_password,
                app=app,
            )

            setattr(
                instance,
                'plain_basicauth_password',
                plain_basicauth_password
            )

        if settings.OCTOPRINT_TUNNEL_PORT_RANGE is not None:
            free_port = OctoPrintTunnel.get_a_free_port()
            if not free_port:
                return None
            instance.port = free_port
        else:
            instance.subdomain_code = token_hex(8)

        instance.save()
        return instance

    @classmethod
    def get_a_free_port(cls):
        occupied = set(OctoPrintTunnel.objects.filter(
            port__isnull=False
        ).values_list('port', flat=True))
        possible = set(settings.OCTOPRINT_TUNNEL_PORT_RANGE)
        free = possible - occupied
        if not free:
            return None
        return free.pop()

    def get_host(self, request):
        if self.subdomain_code:
            host = '{subdomain_code}.tunnels.{site.domain}'.format(
                subdomain_code=self.subdomain_code,
                site=get_current_site(request),
            )
        else:
            host = f'{request.get_host().split(":")[0]}:{self.port}'
        return host

    def get_basicauth_url(self, request, plain_basicauth_password):
        return f'{request.scheme}://{self.basicauth_username}:{plain_basicauth_password}@{self.get_host(request)}'

    def get_internal_tunnel_url(self, request):
        return f'{request.scheme}://{self.get_host(request)}'

    def is_octoprint_connected(self):
        return channels.num_ws_connections(
            channels.octo_group_name(self.printer.id)
        ) > 0


class NotificationSetting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    name = models.TextField()
    config_json = models.TextField(default='', blank=True)

    enabled = models.BooleanField(default=True)

    notify_on_failure_alert = models.BooleanField(blank=True, default=True)

    notify_on_print_done = models.BooleanField(blank=True, default=True)
    notify_on_print_cancelled = models.BooleanField(blank=True, default=False)
    notify_on_filament_change = models.BooleanField(blank=True, default=True)

    notify_on_heater_status = models.BooleanField(blank=True, default=False)

    notify_on_print_start = models.BooleanField(blank=True, default=False)
    notify_on_print_pause = models.BooleanField(blank=True, default=False)
    notify_on_print_resume = models.BooleanField(blank=True, default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def config(self) -> Dict:
        return json.loads(self.config_json) if self.config_json else {}

    class Meta:
        unique_together = ('user', 'name')


@receiver(post_save, sender=User)
def init_email_notification_setting(sender, instance, created, **kwargs):
    if created:
        NotificationSetting.objects.get_or_create(user=instance, name='email')


class FirstLayerInspection(models.Model):
    print = models.ForeignKey(Print, on_delete=models.SET_NULL, null=True)
    score = models.FloatField(null=False)
    video_url = models.CharField(max_length=2000, null=True)
    tagged_video_url = models.CharField(max_length=2000, null=True)
    poster_url = models.CharField(max_length=2000, null=True, blank=True)
    data_json_url = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class FirstLayerInspectionImage(models.Model):
    first_layer_inspection = models.ForeignKey(FirstLayerInspection, on_delete=models.CASCADE, null=False)
    image_url = models.TextField(null=False, blank=False)
    labels = models.TextField(null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
