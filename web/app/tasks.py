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
from django.conf import settings
from django.core import serializers
from celery import shared_task
import tempfile
import requests
from PIL import Image
import copy
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMessage

from .models import *
from lib.file_storage import list_file_obj, retrieve_to_file_obj, save_file_obj
from lib.utils import ml_api_auth_headers
from lib.prediction import update_prediction_with_detections, is_failing, VISUALIZATION_THRESH
from lib.image import overlay_detections

LOGGER = logging.getLogger(__name__)

@shared_task(acks_late=True, bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3}, retry_backoff=True)
def compile_timelapse(self, print_id):
    print = Print.objects.get(id=print_id)
    end_time = print.finished_at or print.cancelled_at

    if (end_time - print.started_at).total_seconds() < settings.TIMELAPSE_MINIMUM_SECONDS:
        print.delete()
        return

    to_dir = os.path.join(tempfile.gettempdir(), str(print.id))
    shutil.rmtree(to_dir, ignore_errors=True)
    os.mkdir(to_dir)

    print_pics = filter_pics_by_start_end(list_file_obj('raw/{}/'.format(print.printer.id), settings.PICS_CONTAINER), print.started_at, end_time)
    print_pics.sort()
    if print_pics:
        local_pics = download_files(print_pics, to_dir)
        last_pic = local_pics[-1]
        mp4_filename = '{}.mp4'.format(print.id)
        output_mp4 = os.path.join(to_dir, mp4_filename)
        subprocess.run('ffmpeg -y -r 30 -pattern_type glob -i {}/*.jpg -c:v libx264 -pix_fmt yuv420p {}'.format(last_pic.parent, output_mp4).split(' '), check=True)
        shutil.copyfile(last_pic, os.path.join(to_dir, '{}.jpg'.format(print.id)))

        with open(output_mp4, 'rb') as mp4_file:
            _, mp4_file_url = save_file_obj('private/{}'.format(mp4_filename), mp4_file, settings.TIMELAPSE_CONTAINER)
        with open(last_pic, 'rb') as poster_file:
            _, poster_file_url = save_file_obj('private/{}_poster.jpg'.format(print.id), poster_file, settings.TIMELAPSE_CONTAINER)

        print.video_url = mp4_file_url
        print.poster_url = poster_file_url
        print.save()

    # build tagged timelapse
    print_pics = filter_pics_by_start_end(list_file_obj('tagged/{}/'.format(print.printer.id), settings.PICS_CONTAINER), print.started_at, end_time)
    print_pics.sort()
    if print_pics:
        local_pics = download_files(print_pics, to_dir)
        mp4_filename = '{}_tagged.mp4'.format(print.id)
        output_mp4 = os.path.join(to_dir, mp4_filename)
        subprocess.run('ffmpeg -y -r 30 -pattern_type glob -i {}/*.jpg -c:v libx264 -pix_fmt yuv420p {}'.format(local_pics[0].parent, output_mp4).split(' '), check=True)
        with open(output_mp4, 'rb') as mp4_file:
            _, mp4_file_url = save_file_obj('private/{}'.format(mp4_filename), mp4_file, settings.TIMELAPSE_CONTAINER)


        json_files = [ print_pic.replace('tagged/', 'p/').replace('.jpg', '.json') for print_pic in print_pics ]
        local_jsons = download_files(json_files, to_dir)
        preidction_json = []
        for p_json_file in local_jsons:
            with open(p_json_file, 'r') as f:
                try:
                    p_json = json.load(f)
                except json.decoder.JSONDecodeError:    # In case there is no corresponding json, the file will be empty and JSONDecodeError will be thrown
                    p_json = [{}]
                preidction_json += p_json
        preidction_json_io = io.BytesIO()
        preidction_json_io.write(json.dumps(preidction_json).encode('UTF-8'))
        preidction_json_io.seek(0)
        _, json_url = save_file_obj('private/{}_p.json'.format(print.id), preidction_json_io, settings.TIMELAPSE_CONTAINER)

        print.tagged_video_url = mp4_file_url
        print.prediction_json_url = json_url
        print.save()

    shutil.rmtree(to_dir, ignore_errors=True)

@shared_task(acks_late=True, bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 2}, retry_backoff=True)
def preprocess_timelapse(self, user_id, video_path, filename, user_credit_id):
        tmp_file_path = os.path.join(tempfile.gettempdir(), video_path)
        converted_mp4_path = tmp_file_path + '.mp4'
        with open(tmp_file_path, 'wb') as file_obj:
            retrieve_to_file_obj(f'uploaded/{video_path}', file_obj, settings.PICS_CONTAINER)

        subprocess.run(f'ffmpeg -y -i {tmp_file_path} -c:v libx264 -pix_fmt yuv420p {converted_mp4_path}'.split(), check=True)

        _print = Print.objects.create(user_id=user_id, filename=filename, uploaded_at=timezone.now())
        with open(converted_mp4_path, 'rb') as mp4_file:
            _, video_url = save_file_obj(f'private/{_print.id}.mp4', mp4_file, settings.TIMELAPSE_CONTAINER)
        _print.video_url = video_url
        _print.save()

        detect_timelapse.delay(_print.id)
        os.remove(tmp_file_path)
        os.remove(converted_mp4_path)
        UserCredit.objects.filter(id=user_credit_id).update(print_id=_print.id)

@shared_task(acks_late=True, bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 2}, retry_backoff=True)
def detect_timelapse(self, print_id):
    MAX_FRAME_NUM = 750

    _print = Print.objects.get(pk=print_id)
    tmp_dir = os.path.join(tempfile.gettempdir(), str(_print.id))
    tl_path = download_files([f'private/{_print.id}.mp4'], tmp_dir, container=settings.TIMELAPSE_CONTAINER)[0]

    jpgs_dir = os.path.join(tmp_dir, 'jpgs')
    shutil.rmtree(jpgs_dir, ignore_errors=True)
    os.makedirs(jpgs_dir)
    tagged_jpgs_dir = os.path.join(tmp_dir, 'tagged_jpgs')
    shutil.rmtree(tagged_jpgs_dir, ignore_errors=True)
    os.makedirs(tagged_jpgs_dir)

    ffprobe_cmd = subprocess.run(f'ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 {tl_path}'.split(), stdout=subprocess.PIPE)
    frame_num = int(ffprobe_cmd.stdout.strip())
    fps = 30*MAX_FRAME_NUM/frame_num if frame_num > MAX_FRAME_NUM else 30
    subprocess.run(f'ffmpeg -i {tl_path} -vf fps={fps} -qscale:v 2 {jpgs_dir}/{print_id}-%5d.jpg'.split())

    predictions = []
    last_prediction = PrinterPrediction()
    jpg_filenames = sorted(os.listdir(jpgs_dir))
    for jpg_path in jpg_filenames:
        jpg_abs_path = os.path.join(jpgs_dir, jpg_path)
        with open(jpg_abs_path, 'rb') as pic:
            internal_url, _ = save_file_obj(f'raw/uploaded_prints/{jpg_path}', pic, settings.PICS_CONTAINER)
            req = requests.get(settings.ML_API_HOST + '/p/', params={'img': internal_url}, headers=ml_api_auth_headers(), verify=False)
            req.raise_for_status()
            detections = req.json()['detections']
            update_prediction_with_detections(last_prediction, detections)
            predictions.append(last_prediction)

            if is_failing(last_prediction, 1, escalating_factor=1):
                _print.alerted_at = timezone.now()

            last_prediction = copy.deepcopy(last_prediction)
            detections_to_visualize = [d for d in detections if d[1] > VISUALIZATION_THRESH]
            overlay_detections(Image.open(jpg_abs_path), detections_to_visualize).save(os.path.join(tagged_jpgs_dir, jpg_path), "JPEG")

    predictions_json = serializers.serialize("json", predictions)
    _, json_url = save_file_obj(f'private/{_print.id}_p.json', io.BytesIO(str.encode(predictions_json)), settings.TIMELAPSE_CONTAINER)

    mp4_filename = f'{_print.id}_tagged.mp4'
    output_mp4 = os.path.join(tmp_dir, mp4_filename)
    subprocess.run(f'ffmpeg -y -r 30 -pattern_type glob -i {tagged_jpgs_dir}/*.jpg -c:v libx264 -pix_fmt yuv420p {output_mp4}'.split(), check=True)
    with open(output_mp4, 'rb') as mp4_file:
        _, mp4_file_url = save_file_obj(f'private/{mp4_filename}', mp4_file, settings.TIMELAPSE_CONTAINER)

    with open(os.path.join(jpgs_dir, jpg_filenames[-1]), 'rb') as poster_file:
        _, poster_file_url = save_file_obj(f'private/{_print.id}_poster.jpg', poster_file, settings.TIMELAPSE_CONTAINER)

    _print.tagged_video_url = mp4_file_url
    _print.prediction_json_url = json_url
    _print.poster_url = poster_file_url
    _print.save()

    shutil.rmtree(tmp_dir, ignore_errors=True)
    send_timelapse_detection_done_email(_print)

# helper functions

def download_files(filenames, to_dir, container=settings.PICS_CONTAINER):
    output_files = []
    for filename in filenames:
        output_path = Path(os.path.join(to_dir, filename))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as file_obj:
            retrieve_to_file_obj(filename, file_obj, container)
        output_files += [output_path]

    return output_files

def filter_pics_by_start_end(pic_files, start_time, end_time):
    start_ts = start_time.timestamp()
    end_ts = end_time.timestamp()
    filtered_pic_files = []
    for pic_file in pic_files:
        matched = re.search('/(\d+).jpg', pic_file)
        if not matched:
            continue
        timestamp = int(matched[1])
        if start_ts <= timestamp <= end_ts:
            filtered_pic_files += [pic_file]

    return filtered_pic_files

def send_timelapse_detection_done_email(_print):
    if not settings.EMAIL_HOST:
        LOGGER.warn("Email settings are missing. Ignored send requests")
        return

    subject = 'The Detective is done looking at the time-lapse you uploaded.'
    from_email = settings.DEFAULT_FROM_EMAIL

    ctx = {
        'print': _print,
    }
    emails = [email.email for email in EmailAddress.objects.filter(user=_print.user)]
    message = get_template('email/upload_print_processed.html').render(ctx)
    msg = EmailMessage(subject, message, to=emails, from_email=from_email)
    msg.content_subtype = 'html'
    msg.send()
