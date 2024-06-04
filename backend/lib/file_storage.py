from datetime import datetime, timedelta
from django.conf import settings
import base64
from six.moves.urllib.parse import urlencode, quote

import importlib

lt_file_storage = importlib.import_module(settings.LT_FILE_STORAGE_MODULE)
st_file_storage = importlib.import_module(settings.ST_FILE_STORAGE_MODULE)

def save_file_obj(dest_path, file_obj, container, syndicate_name, long_term_storage=True):
    content_type='application/octet-stream'
    if dest_path.endswith('.jpg'):
        content_type='image/jpeg'
    if dest_path.endswith('.mp4'):
        content_type='video/mp4'

    file_storage = lt_file_storage if long_term_storage else st_file_storage
    return file_storage.save_file_obj(dest_path, file_obj, container, syndicate_name, content_type)

def list_dir(dir_path, container, long_term_storage=True):
    file_storage = lt_file_storage if long_term_storage else st_file_storage
    return file_storage.list_dir(dir_path, container)

# Note: silently ignore error if src_path does not exist
def retrieve_to_file_obj(src_path, file_obj, container, long_term_storage=True):
    file_storage = lt_file_storage if long_term_storage else st_file_storage
    return file_storage.retrieve_to_file_obj(src_path, file_obj, container)

def delete_dir(dir_path, container, long_term_storage=True):
    file_storage = lt_file_storage if long_term_storage else st_file_storage
    return file_storage.delete_dir(dir_path, container)

def delete_file(file_path, container, long_term_storage=True):
    file_storage = lt_file_storage if long_term_storage else st_file_storage
    return file_storage.delete_file(file_path, container)
