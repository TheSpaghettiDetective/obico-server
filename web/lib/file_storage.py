from datetime import datetime, timedelta
from django.conf import settings
from google.cloud import storage
from oauth2client.service_account import ServiceAccountCredentials
import base64
from six.moves.urllib.parse import urlencode, quote

import importlib

lt_file_storage = importlib.import_module(getattr(settings, 'LT_FILE_STORAGE_MODULE', 'lib.fs_file_storage'))
st_file_storage = importlib.import_module(getattr(settings, 'ST_FILE_STORAGE_MODULE', 'lib.fs_file_storage'))

def save_file_obj(dest_path, file_obj, container, return_url=True, long_term_storage=True):
    file_storage = lt_file_storage if long_term_storage else st_file_storage
    return file_storage.save_file_obj(dest_path, file_obj, container, return_url)

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
