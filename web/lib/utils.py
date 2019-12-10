
import json
from django.conf import settings

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
    orientation = (printer_settings['webcam_flipV'], printer_settings['webcam_flipH'],printer_settings['webcam_rotate90'])
    if orientation == (False, False, True):
        return '-vf transpose=2'
    elif orientation == (False, True, False):
        return '-vf hflip'
    elif orientation == (False, True, True):
        return '-vf transpose=0'
    elif orientation == (True, False, False):
        return '-vf vflip'
    elif orientation == (True, False, True):
        return '-vf transpose=3'
    elif orientation == (True, True, True):
        return '-vf transpose=1'
    elif orientation == (True, True, False):
        return '-vf hflip,vflip'
    else:
        return ''
