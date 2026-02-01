# Create your tasks here
from __future__ import absolute_import, unicode_literals
import re
import os
import io
import json
import subprocess
from pathlib import Path
import shutil
import logging
from django.utils import timezone
from django.conf import settings
from django.core import serializers
from celery import shared_task
from config.celery import PeriodicTask
from datetime import timedelta
import tempfile
import requests
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import copy
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage
from channels_presence.models import Room

from .models import *
from .models import Print, PrinterEvent
from lib.file_storage import list_dir, retrieve_to_file_obj, save_file_obj, delete_dir
from lib.utils import ml_api_auth_headers, orientation_to_ffmpeg_options, copy_pic, last_pic_of_print
from lib.prediction import update_prediction_with_detections, is_failing, VISUALIZATION_THRESH
from lib.image import overlay_detections
from lib import cache
from lib import syndicate
from notifications.handlers import handler
from notifications import notification_types
from api.octoprint_views import IMG_URL_TTL_SECONDS

LOGGER = logging.getLogger(__name__)


@shared_task
def process_print_events(event_id):
    print_event = PrinterEvent.objects.select_related('print').get(id=event_id)
    if print_event.event_type == PrinterEvent.ENDED:
        process_print_end_event(print_event)
    else:
        send_notification_for_print_event(print_event.print, print_event)


def process_print_end_event(print_event):
    _print = Print.objects.select_related('printer__user').get(id=print_event.print_id)

    _print.poster_url = print_event.image_url
    _print.save()

    if will_record_timelapse(_print):
        select_print_shots_for_feedback(_print)
        send_notification_for_print_event(_print, print_event)
        compile_timelapse.delay(print_event.print_id)


def send_notification_for_print_event(_print, print_event, extra_context=None):
    notification_type = notification_types.from_print_event(print_event)
    if notification_type:
        handler.queue_send_printer_notifications_task(
            printer=print_event.printer,
            notification_type=notification_type,
            print_=_print,
            img_url=print_event.image_url,
            extra_context=extra_context,
            in_process=True,
        )


@shared_task(acks_late=True)
def compile_timelapse(print_id):
    _print = Print.objects.all_with_deleted().select_related('printer').get(id=print_id)

    to_dir = os.path.join(tempfile.gettempdir(), 'tl_' + str(_print.id))
    shutil.rmtree(to_dir, ignore_errors=True)
    os.mkdir(to_dir)

    ffmpeg_extra_options = orientation_to_ffmpeg_options(_print.printer.settings)
    pic_dir = f'{_print.printer.id}/{_print.id}'

    print_pics = list_dir(f'raw/{pic_dir}/', settings.PICS_CONTAINER, long_term_storage=False)
    print_pics.sort()
    if print_pics:
        local_pics = download_files(print_pics, to_dir)
        mp4_filename = '{}.mp4'.format(_print.id)
        output_mp4 = os.path.join(to_dir, mp4_filename)
        cmd = 'ffmpeg -y -r 30 -pattern_type glob -i {}/*.jpg -c:v libx264 -pix_fmt yuv420p {} {}'.format(local_pics[-1].parent, ffmpeg_extra_options, output_mp4)
        subprocess.run(cmd.split(), check=True)

        with open(output_mp4, 'rb') as mp4_file:
            _, mp4_file_url = save_file_obj('private/{}'.format(mp4_filename), mp4_file, settings.TIMELAPSE_CONTAINER, _print.user.syndicate.name)

        _print.video_url = mp4_file_url
        _print.save(keep_deleted=True)

    # build tagged timelapse
    print_pics = list_dir(f'tagged/{pic_dir}/', settings.PICS_CONTAINER, long_term_storage=False)
    print_pics.sort()
    if print_pics:
        local_pics = download_files(print_pics, to_dir)
        mp4_filename = '{}_tagged.mp4'.format(_print.id)
        output_mp4 = os.path.join(to_dir, mp4_filename)
        cmd = 'ffmpeg -y -r 30 -pattern_type glob -i {}/*.jpg -c:v libx264 -pix_fmt yuv420p -vf pad=ceil(iw/2)*2:ceil(ih/2)*2 {} {}'.format(
            local_pics[0].parent, ffmpeg_extra_options, output_mp4)
        subprocess.run(cmd.split(), check=True)
        with open(output_mp4, 'rb') as mp4_file:
            _, mp4_file_url = save_file_obj('private/{}'.format(mp4_filename), mp4_file, settings.TIMELAPSE_CONTAINER, _print.user.syndicate.name)

        json_files = list_dir(f'p/{pic_dir}/', settings.PICS_CONTAINER, long_term_storage=False)
        local_jsons = download_files(json_files, to_dir)
        prediction_json = []
        num_missing_p_json = 0
        for pic_path in local_pics:
            try:
                with open(str(pic_path).replace('tagged/', 'p/').replace('.jpg', '.json'), 'r') as f:
                    p_json = json.load(f)
            except (FileNotFoundError, json.decoder.JSONDecodeError) as e:    # In case there is no corresponding json, the file will be empty and JSONDecodeError will be thrown
                LOGGER.warn(e)
                p_json = [{}]
                num_missing_p_json += 1
                if num_missing_p_json > 5:
                    shutil.rmtree(to_dir, ignore_errors=True)
                    clean_up_print_pics(_print)
                    raise Exception('Too many missing p_json files.')

            prediction_json += p_json
        prediction_json_io = io.BytesIO()
        prediction_json_io.write(json.dumps(prediction_json).encode('UTF-8'))
        prediction_json_io.seek(0)
        _, json_url = save_file_obj('private/{}_p.json'.format(_print.id), prediction_json_io, settings.TIMELAPSE_CONTAINER, _print.user.syndicate.name)

        _print.tagged_video_url = mp4_file_url
        _print.prediction_json_url = json_url
        _print.save(keep_deleted=True)

    shutil.rmtree(to_dir, ignore_errors=True)
    clean_up_print_pics(_print)


@shared_task(acks_late=True, bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 2}, retry_backoff=True)
def preprocess_timelapse(self, user_id, video_path, filename):
    tmp_file_path = os.path.join(tempfile.gettempdir(), video_path)
    converted_mp4_path = tmp_file_path + '.mp4'
    Path(tmp_file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(tmp_file_path, 'wb') as file_obj:
        retrieve_to_file_obj(f'uploaded/{video_path}', file_obj, settings.TIMELAPSE_CONTAINER, long_term_storage=True)

    subprocess.run(f'ffmpeg -y -i {tmp_file_path} -c:v libx264 -pix_fmt yuv420p {converted_mp4_path}'.split(), check=True)

    _print = Print.objects.create(user_id=user_id, filename=filename, uploaded_at=timezone.now(), started_at=timezone.now(), finished_at=timezone.now())
    with open(converted_mp4_path, 'rb') as mp4_file:
        _, video_url = save_file_obj(f'private/{_print.id}.mp4', mp4_file, settings.TIMELAPSE_CONTAINER, _print.user.syndicate.name)
    _print.video_url = video_url
    _print.save(keep_deleted=True)

    detect_timelapse.delay(_print.id)
    os.remove(tmp_file_path)
    os.remove(converted_mp4_path)


@shared_task(acks_late=True, bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 2}, retry_backoff=True)
def detect_timelapse(self, print_id):
    MAX_FRAME_NUM = 750

    _print = Print.objects.get(pk=print_id)
    tmp_dir = os.path.join(tempfile.gettempdir(), str(_print.id))
    mp4_filepath = f'private/{_print.id}.mp4'
    tl_path = os.path.join(tmp_dir, mp4_filepath)
    Path(tl_path).parent.mkdir(parents=True, exist_ok=True)
    with open(tl_path, 'wb') as file_obj:
        retrieve_to_file_obj(mp4_filepath, file_obj, settings.TIMELAPSE_CONTAINER)

    jpgs_dir = os.path.join(tmp_dir, 'jpgs')
    shutil.rmtree(jpgs_dir, ignore_errors=True)
    os.makedirs(jpgs_dir)
    tagged_jpgs_dir = os.path.join(tmp_dir, 'tagged_jpgs')
    shutil.rmtree(tagged_jpgs_dir, ignore_errors=True)
    os.makedirs(tagged_jpgs_dir)

    ffprobe_cmd = subprocess.run(
        f'ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 {tl_path}'.split(), stdout=subprocess.PIPE)
    frame_num = int(ffprobe_cmd.stdout.strip())
    fps = 30*MAX_FRAME_NUM/frame_num if frame_num > MAX_FRAME_NUM else 30
    subprocess.run(f'ffmpeg -y -i {tl_path} -vf fps={fps} -qscale:v 2 {jpgs_dir}/%5d.jpg'.split())

    predictions = []
    last_prediction = PrinterPrediction()
    jpg_filenames = sorted(os.listdir(jpgs_dir))
    for jpg_path in jpg_filenames:
        jpg_abs_path = os.path.join(jpgs_dir, jpg_path)
        with open(jpg_abs_path, 'rb') as pic:
            pic_path = f'{_print.user.id}/{_print.id}/{jpg_path}'
            internal_url, _ = save_file_obj(f'uploaded/{pic_path}', pic, settings.PICS_CONTAINER, _print.user.syndicate.name, long_term_storage=False)
            req = requests.get(settings.ML_API_HOST + '/p/', params={'img': internal_url}, headers=ml_api_auth_headers(), verify=False)
            req.raise_for_status()
            detections = req.json()['detections']
            update_prediction_with_detections(last_prediction, detections, _print.printer)
            predictions.append(last_prediction)

            if is_failing(last_prediction, 1, escalating_factor=1):
                _print.alerted_at = timezone.now()

            last_prediction = copy.deepcopy(last_prediction)
            detections_to_visualize = [d for d in detections if d[1] > VISUALIZATION_THRESH]
            overlay_detections(Image.open(jpg_abs_path), detections_to_visualize).save(os.path.join(tagged_jpgs_dir, jpg_path), "JPEG")

    predictions_json = serializers.serialize("json", predictions)
    _, json_url = save_file_obj(f'private/{_print.id}_p.json', io.BytesIO(str.encode(predictions_json)), settings.TIMELAPSE_CONTAINER, _print.user.syndicate.name)

    mp4_filename = f'{_print.id}_tagged.mp4'
    output_mp4 = os.path.join(tmp_dir, mp4_filename)
    subprocess.run(
        f'ffmpeg -y -r 30 -pattern_type glob -i {tagged_jpgs_dir}/*.jpg -c:v libx264 -pix_fmt yuv420p -vf pad=ceil(iw/2)*2:ceil(ih/2)*2 {output_mp4}'.split(), check=True)
    with open(output_mp4, 'rb') as mp4_file:
        _, mp4_file_url = save_file_obj(f'private/{mp4_filename}', mp4_file, settings.TIMELAPSE_CONTAINER, _print.user.syndicate.name)

    with open(os.path.join(jpgs_dir, jpg_filenames[-1]), 'rb') as poster_file:
        _, poster_file_url = save_file_obj(f'private/{_print.id}_poster.jpg', poster_file, settings.TIMELAPSE_CONTAINER, _print.user.syndicate.name)

    _print.tagged_video_url = mp4_file_url
    _print.prediction_json_url = json_url
    _print.poster_url = poster_file_url
    _print.save(keep_deleted=True)

    shutil.rmtree(tmp_dir, ignore_errors=True)
    send_timelapse_detection_done_email(_print)
    delete_dir(f'uploaded/{_print.user.id}/{_print.id}/', settings.PICS_CONTAINER, long_term_storage=False)


# Websocket connection count house upkeep jobs

@shared_task(base=PeriodicTask, run_every=timedelta(seconds=1200))
def prune_channel_presence():
    Room.objects.prune_presences(age=120)


@shared_task(base=PeriodicTask, run_every=timedelta(seconds=1200))
def prune_channel_rooms():
    Room.objects.prune_rooms()


# helper functions


def download_files(filenames, to_dir, container=settings.PICS_CONTAINER):
    output_files = []
    for filename in filenames:
        output_path = Path(os.path.join(to_dir, filename))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as file_obj:
            retrieve_to_file_obj(filename, file_obj, container, long_term_storage=False)

        output_files += [output_path]

    return output_files


def clean_up_print_pics(_print):
    pic_dir = f'{_print.printer.id}/{_print.id}'
    delete_dir('raw/{}/'.format(pic_dir), settings.PICS_CONTAINER, long_term_storage=False)
    delete_dir('tagged/{}/'.format(pic_dir), settings.PICS_CONTAINER, long_term_storage=False)
    delete_dir('p/{}/'.format(pic_dir), settings.PICS_CONTAINER, long_term_storage=False)


def will_record_timelapse(_print):
    last_pic = last_pic_of_print(_print, 'raw')

    if not last_pic: # This print does not have any raw pics
        return False

    # Save the unrotated snapshot so that it is still viewable even after the print is done.
    unrotated_jpg_url = copy_pic(
                            last_pic,
                            f'snapshots/{_print.printer.id}/latest_unrotated.jpg',
                            _print.user.syndicate.name,
                            rotated=False,
                            to_long_term_storage=False
                        )
    cache.printer_pic_set(_print.printer.id, {'img_url': unrotated_jpg_url}, ex=IMG_URL_TTL_SECONDS)

    min_timelapse_secs = _print.printer.min_timelapse_secs_on_cancel if _print.is_canceled() else _print.printer.min_timelapse_secs_on_finish
    if min_timelapse_secs < 0 or (_print.ended_at() - _print.started_at).total_seconds() < min_timelapse_secs:
        clean_up_print_pics(_print)
        return False

    return True

def send_timelapse_detection_done_email(_print):
    syndicate_name = _print.user.syndicate.name
    if syndicate_name != 'base':
        return
    if not settings.EMAIL_HOST:
        LOGGER.warn("Email settings are missing. Ignored send requests")
        return

    subject = 'We are done detecting failures on the time-lapse you uploaded.'
    from_email = settings.DEFAULT_FROM_EMAIL

    ctx = {
        'print': _print,
        'unsub_url': 'https://app.obico.io/ent/email_unsubscribe/?list=notification&email={}'.format(_print.user.email),
        'prints_link': syndicate.build_full_url_for_syndicate('/print_history/', syndicate_name),
    }
    emails = [email.email for email in EmailAddress.objects.filter(user=_print.user)]
    message = get_template('email/upload_print_processed.html').render(ctx)
    msg = EmailMessage(subject, message,
                    to=emails,
                    from_email=from_email,
                    headers={'List-Unsubscribe': '<{}>, <mailto:support@obico.io?subject=Unsubscribe_notification>'.format(ctx['unsub_url'])},
                    )
    msg.content_subtype = 'html'
    msg.send()


def select_print_shots_for_feedback(_print):

    # Select up to 7 highest predictions that are apart from each other for at least 2 minutes
    def highest_7_predictions(prediction_list):
        selected_timestamps = []

        for pred in prediction_list:
            pred_ts = float(pred[0])
            if len([ts for ts in selected_timestamps if abs(ts - pred_ts) < 120]) > 0:   # timestamp is within 2 minutes from one other selected predictions
                continue

            selected_timestamps += [pred_ts]
            if len(selected_timestamps) >= 7:
                break

        return sorted(selected_timestamps)

    for ts in highest_7_predictions(cache.print_highest_predictions_get(_print.id)):
        rotated_jpg_url = copy_pic(
                            f'raw/{_print.printer.id}/{_print.id}/{ts}.jpg',
                            f'ff_printshots/{_print.user.id}/{_print.id}/{ts}.jpg',
                            _print.user.syndicate.name,
                            rotated=True,
                            printer_settings=_print.printer.settings,
                            to_long_term_storage=False
                        )
        PrintShotFeedback.objects.create(print=_print, image_url=rotated_jpg_url)
