
import json
from django.conf import settings
import subprocess
import tempfile
import os
import shutil
from operator import itemgetter

from lib.file_storage import list_dir, retrieve_to_file_obj, save_file_obj

# Return dict if not empty, otherwise None.


def dict_or_none(dict_value):
    return dict_value if dict_value else None


def set_as_str_if_present(target_dict, source_dict, key, target_key=None):
    if source_dict.get(key):
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


def last_pic_of_print(_print, path_prefix):
    print_pics = list_dir(f'{path_prefix}/{_print.printer.id}/{_print.id}/', settings.PICS_CONTAINER, long_term_storage=False)
    if not print_pics:
        return None
    print_pics.sort()
    return print_pics[-1]


def save_print_snapshot(_print, input_path, unrotated_jpg_path=None, rotated_jpg_path=None):
    if not input_path:
        return (None, None)

    to_dir = os.path.join(tempfile.gettempdir(), str(_print.id))
    shutil.rmtree(to_dir, ignore_errors=True)
    os.mkdir(to_dir)
    unrotated_jpg = os.path.join(to_dir, 'unrotated.jpg')
    with open(unrotated_jpg, 'wb') as file_obj:
        retrieve_to_file_obj(input_path, file_obj, settings.PICS_CONTAINER, long_term_storage=False)

    (unrotated_jpg_url, rotated_jpg_url) = (None, None)

    if unrotated_jpg_path:
        with open(unrotated_jpg, 'rb') as file_obj:
            _, unrotated_jpg_url = save_file_obj(unrotated_jpg_path, file_obj, settings.TIMELAPSE_CONTAINER)

    if rotated_jpg_path:
        ffmpeg_extra_options = orientation_to_ffmpeg_options(_print.printer.settings)
        rotated_jpg = os.path.join(to_dir, 'rotated.jpg')
        cmd = f'ffmpeg -y -i {unrotated_jpg} {ffmpeg_extra_options} {rotated_jpg}'
        subprocess.run(cmd.split(), check=True)
        with open(rotated_jpg, 'rb') as file_obj:
            _, rotated_jpg_url = save_file_obj(rotated_jpg_path, file_obj, settings.TIMELAPSE_CONTAINER)

        shutil.rmtree(to_dir, ignore_errors=True)

    return (unrotated_jpg_url, rotated_jpg_url)
