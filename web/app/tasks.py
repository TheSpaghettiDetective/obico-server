# Create your tasks here
from __future__ import absolute_import, unicode_literals
import re
import os
import io
import json
import subprocess
from pathlib import Path
import shutil
from django.conf import settings
from celery import shared_task
import tempfile

from .models import *
from lib.file_storage import list_file_obj, retrieve_to_file_obj, save_file_obj

@shared_task(acks_late=True, bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3}, retry_backoff=True)
def compile_timelapse(self, print_id):
    pprint = Print.objects.get(id=print_id)
    end_time = pprint.finished_at or pprint.cancelled_at

    to_dir = os.path.join(tempfile.gettempdir(), str(pprint.id))
    shutil.rmtree(to_dir, ignore_errors=True)
    os.mkdir(to_dir)

    print_pics = filter_pics_by_start_end(list_file_obj('raw/{}/'.format(pprint.printer.id), settings.PICS_CONTAINER), pprint.started_at, end_time)
    print_pics.sort()
    if print_pics:
        local_pics = download_files(print_pics, to_dir)
        last_pic = local_pics[-1]
        mp4_filename = '{}.mp4'.format(pprint.id)
        output_mp4 = os.path.join(to_dir, mp4_filename)
        subprocess.run('ffmpeg -y -pattern_type glob -i {}/*.jpg -c:v libx264 -vf fps=30 -pix_fmt yuv420p {}'.format(last_pic.parent, output_mp4).split(' '), check=True)
        shutil.copyfile(last_pic, os.path.join(to_dir, '{}.jpg'.format(pprint.id)))

        with open(output_mp4, 'rb') as mp4_file:
            _, mp4_file_url = save_file_obj('private/{}'.format(mp4_filename), mp4_file, settings.TIMELAPSE_CONTAINER)
        with open(last_pic, 'rb') as poster_file:
            _, poster_file_url = save_file_obj('private/{}_poster.jpg'.format(pprint.id), poster_file, settings.TIMELAPSE_CONTAINER)

        pprint.video_url = mp4_file_url
        pprint.poster_url = poster_file_url
        pprint.save()

    # build tagged timelapse
    print_pics = filter_pics_by_start_end(list_file_obj('tagged/{}/'.format(pprint.printer.id), settings.PICS_CONTAINER), pprint.started_at, end_time)
    print_pics.sort()
    if print_pics:
        local_pics = download_files(print_pics, to_dir)
        mp4_filename = '{}_tagged.mp4'.format(pprint.id)
        output_mp4 = os.path.join(to_dir, mp4_filename)
        subprocess.run('ffmpeg -y -pattern_type glob -i {}/*.jpg -c:v libx264 -vf fps=30 -pix_fmt yuv420p {}'.format(local_pics[0].parent, output_mp4).split(' '), check=True)
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
        _, json_url = save_file_obj('private/{}_p.json'.format(pprint.id), preidction_json_io, settings.TIMELAPSE_CONTAINER)

        pprint.tagged_video_url = mp4_file_url
        pprint.prediction_json_url = json_url
        pprint.save()

    shutil.rmtree(to_dir, ignore_errors=True)

def download_files(filenames, to_dir):
    output_files = []
    for filename in filenames:
        output_path = Path(os.path.join(to_dir, filename))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as file_obj:
            retrieve_to_file_obj(filename, file_obj, settings.PICS_CONTAINER)
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
