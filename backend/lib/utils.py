
import json
from django.conf import settings
import subprocess
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

    rotation = printer_settings['webcam_rotation']
    flip = (printer_settings['webcam_flipV'], printer_settings['webcam_flipH'])

    if rotation == 90:
        options += ',transpose=1'
    elif rotation == 270:
        options += ',transpose=2'
    elif rotation == 180:
        options += ',transpose=1,transpose=1'

    if printer_settings['webcam_flipV']:
        options += ',vflip'

    if printer_settings['webcam_flipH']:
        options += ',hflip'

    return options

def shortform_duration(total_seconds):
    if not total_seconds:
        return '--:--'
    total_seconds = int(total_seconds)
    hours, remainder = divmod(total_seconds,60*60)
    minutes, seconds = divmod(remainder,60)
    return '{:02}:{:02}'.format(hours, minutes)

def shortform_localtime(seconds_from_now, tz):
    if not seconds_from_now:
        return '--:--'

    return (timezone.now() + timedelta(seconds=seconds_from_now)).astimezone(pytz.timezone(tz)).strftime("%I:%M%p")


## util functions for pictures

def last_pic_of_print(_print, path_prefix):
    print_pics = list_dir(f'{path_prefix}/{_print.printer.id}/{_print.id}/', settings.PICS_CONTAINER, long_term_storage=False)
    if not print_pics:
        return None
    print_pics.sort()
    return print_pics[-1]


def copy_pic(input_path, dest_jpg_path, syndicate_name, rotated=False, printer_settings=None, to_container=settings.PICS_CONTAINER, to_long_term_storage=True):
    if not input_path:
        return None

    img_bytes = io.BytesIO()
    retrieve_to_file_obj(input_path, img_bytes, settings.PICS_CONTAINER, long_term_storage=False)
    img_bytes.seek(0)
    return save_pic(dest_jpg_path, img_bytes, syndicate_name, rotated=rotated, printer_settings=printer_settings, to_container=to_container, to_long_term_storage=to_long_term_storage)


def save_pic(dest_jpg_path, img_bytes, syndicate_name, rotated=False, printer_settings=None, to_container=settings.PICS_CONTAINER, to_long_term_storage=True):
    bytes_to_save = img_bytes

    if rotated:
        tmp_img = Image.open(bytes_to_save)
        if printer_settings['webcam_flipH']:
            tmp_img = tmp_img.transpose(Image.FLIP_LEFT_RIGHT)
        if printer_settings['webcam_flipV']:
            tmp_img = tmp_img.transpose(Image.FLIP_TOP_BOTTOM)
        if printer_settings['webcam_rotation'] and printer_settings['webcam_rotation'] != 0:
            tmp_img = tmp_img.rotate(-printer_settings['webcam_rotation'], expand=True)

        bytes_to_save = io.BytesIO()
        tmp_img.save(bytes_to_save, "JPEG")
        bytes_to_save.seek(0)

    _, dest_jpg_url = save_file_obj(dest_jpg_path, bytes_to_save, to_container, syndicate_name, long_term_storage=to_long_term_storage)
    return dest_jpg_url


def get_rotated_pic_url(printer, jpg_url=None, force_snapshot=False):
    if not jpg_url:
        if not printer.pic or not printer.pic.get('img_url'):
            return None
        jpg_url = printer.pic.get('img_url')

    need_rotation = printer.settings['webcam_flipV'] or printer.settings['webcam_flipH'] \
        or (printer.settings['webcam_rotation'] and printer.settings['webcam_rotation'] != 0)

    if not need_rotation and not force_snapshot:
        return jpg_url

    jpg_path = re.search(f'{settings.PICS_CONTAINER}/(raw/\d+/[\d\.\/]+.jpg|tagged/\d+/[\d\.\/]+.jpg|snapshots/\d+/\w+.jpg)', jpg_url)

    file_prefix = str(timezone.now().timestamp()) if force_snapshot else 'latest'
    return copy_pic(
                jpg_path.group(1),
                f'snapshots/{printer.id}/{file_prefix}_rotated.jpg',
                syndicate_name=printer.user.syndicate.name,
                rotated=not 'latest_rotated' in jpg_url,
                printer_settings=printer.settings,
                to_long_term_storage=False
            )
