# Create your tasks here
from __future__ import absolute_import, unicode_literals
import re
import os
import subprocess
from pathlib import Path
import shutil
from django.conf import settings
from celery import shared_task
import tempfile

from .models import *
from lib.file_storage import list_file_obj, retrieve_to_file_obj, save_file_obj

@shared_task(acks_late=True)
def compile_timelapse(print_id):
    print = Print.objects.get(id=print_id)
    start_ts = print.started_at.timestamp()
    end_time = print.finished_at or print.cancelled_at
    end_ts = end_time.timestamp()

    to_dir = os.path.join(tempfile.gettempdir(), str(print.id))
    shutil.rmtree(to_dir, ignore_errors=True)
    os.mkdir(to_dir)

    print_pics = []
    for filename in list_file_obj('raw/{}/'.format(print.printer.id), settings.PICS_CONTAINER):
        timestamp = int(re.search('/(\d+).jpg', filename)[1])
        if start_ts <= timestamp <= end_ts:
            print_pics += [filename]

    if print_pics:
        local_pics = download_pics(print_pics, to_dir)
        last_pic = local_pics[-1]
        mp4_filename = '{}.mp4'.format(print.id)
        output_mp4 = os.path.join(to_dir, mp4_filename)
        subprocess.run('ffmpeg -y -pattern_type glob -i {}/*.jpg -c:v libx264 -vf fps=30 -pix_fmt yuv420p {}'.format(last_pic.parent, output_mp4).split(' '), check=True)
        shutil.copyfile(last_pic, os.path.join(to_dir, '{}.jpg'.format(print.id)))

        with open(output_mp4, 'rb') as mp4_file:
            mp4_file_url, _ = save_file_obj('private/videos/{}'.format(mp4_filename), mp4_file, settings.TIMELAPSE_CONTAINER)
        with open(last_pic, 'rb') as poster_file:
            poster_file_url, _ = save_file_obj('private/posters/{}.jpg'.format(print.id), poster_file, settings.TIMELAPSE_CONTAINER)

        print.video_url = mp4_file_url
        print.poster_url = poster_file_url
        print.save()

    shutil.rmtree(to_dir, ignore_errors=True)

def download_pics(print_pics, to_dir):
    output_files = []
    for pic_file in sorted(print_pics):
        output_path = Path(os.path.join(to_dir, pic_file))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as file_obj:
            retrieve_to_file_obj(pic_file, file_obj, settings.PICS_CONTAINER)
        output_files += [output_path]

    return output_files
