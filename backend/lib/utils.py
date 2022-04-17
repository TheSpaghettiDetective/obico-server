
import json
from django.conf import settings
import subprocess
import tempfile
import os
import io
import re
import shutil
from operator import itemgetter
from django.utils import timezone
import pytz
from datetime import timedelta
from PIL import Image, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import backoff

from lib.file_storage import list_dir, retrieve_to_file_obj, save_file_obj

# Return dict if not empty, otherwise None.
def dict_or_none(dict_value):
    return dict_value if dict_value else None


def set_as_str_if_present(target_dict, source_dict, key, target_key=None):
    if key in source_dict:
        if not target_key:
            target_key = key
        target_dict[target_key] = json.dumps(source_dict.get(key))


def ml_api_auth_headers():
    return {"Authorization": "Bearer {}".format(settings.ML_API_TOKEN)} if settings.ML_API_TOKEN else {}


def orientation_to_ffmpeg_options(printer_settings):
    options = '-vf pad=ceil(iw/2)*2:ceil(ih/2)*2'
    orientation = (printer_settings['webcam_flipV'], printer_settings['webcam_flipH'], printer_settings['webcam_rotate90'])
    if orientation == (False, False, True):
        options += ',transpose=2'
    elif orientation == (False, True, False):
        options += ',hflip'
    elif orientation == (False, True, True):
        options += ',transpose=0'
    elif orientation == (True, False, False):
        options += ',vflip'
    elif orientation == (True, False, True):
        options += ',transpose=3'
    elif orientation == (True, True, True):
        options += ',transpose=1'
    elif orientation == (True, True, False):
        options += ',hflip,vflip'

    return options

def shortform_duration(total_seconds):
    if not total_seconds:
        return '--:--'
    hours, remainder = divmod(total_seconds,60*60)
    minutes, seconds = divmod(remainder,60)
    return '{:02}:{:02}'.format(hours, minutes)

def shortform_localtime(seconds_from_now, tz):
    if not seconds_from_now:
        return '--:--'

    return (timezone.now() + timedelta(seconds=seconds_from_now)).astimezone(pytz.timezone(tz)).strftime("%I:%M%p")


## util functions for printer snapshot

def last_pic_of_print(_print, path_prefix):
    print_pics = list_dir(f'{path_prefix}/{_print.printer.id}/{_print.id}/', settings.PICS_CONTAINER, long_term_storage=False)
    if not print_pics:
        return None
    print_pics.sort()
    return print_pics[-1]


def save_print_snapshot(printer, input_path, dest_jpg_path, rotated=False, to_container=settings.PICS_CONTAINER, to_long_term_storage=True):
    if not input_path:
        return None

    img_bytes = io.BytesIO()
    retrieve_to_file_obj(input_path, img_bytes, settings.PICS_CONTAINER, long_term_storage=False)
    img_bytes.seek(0)
    tmp_img = Image.open(img_bytes)
    if rotated:
        if printer.settings['webcam_flipH']:
            tmp_img = tmp_img.transpose(Image.FLIP_LEFT_RIGHT)
        if printer.settings['webcam_flipV']:
            tmp_img = tmp_img.transpose(Image.FLIP_TOP_BOTTOM)
        if printer.settings['webcam_rotate90']:
            tmp_img = tmp_img.transpose(Image.ROTATE_90)

    img_bytes = io.BytesIO()
    tmp_img.save(img_bytes, "JPEG")
    img_bytes.seek(0)
    _, dest_jpg_url = save_file_obj(dest_jpg_path, img_bytes, to_container, long_term_storage=to_long_term_storage)
    return dest_jpg_url


def get_rotated_jpg_url(printer, force_snapshot=False):
    if not printer.pic or not printer.pic.get('img_url'):
        return None
    jpg_url = printer.pic.get('img_url')

    need_rotation = printer.settings['webcam_flipV'] or printer.settings['webcam_flipH'] or printer.settings['webcam_rotate90']

    if not need_rotation and not force_snapshot:
        return jpg_url

    jpg_path = re.search('tsd-pics/(raw/\d+/[\d\.\/]+.jpg|tagged/\d+/[\d\.\/]+.jpg|snapshots/\d+/\w+.jpg)', jpg_url)
    return save_print_snapshot(printer,
                        jpg_path.group(1),
                        f'snapshots/{printer.id}/latest_rotated.jpg',
                        rotated=not 'latest_rotated' in jpg_url,
                        to_long_term_storage=False)