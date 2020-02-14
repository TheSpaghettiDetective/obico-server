
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
    options = '-vf pad=ceil(iw/2)*2:ceil(ih/2)*2'
    orientation = (printer_settings['webcam_flipV'], printer_settings['webcam_flipH'],printer_settings['webcam_rotate90'])
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
