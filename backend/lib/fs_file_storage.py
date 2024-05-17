from django.conf import settings
import os
from os import path
from shutil import copyfileobj, rmtree

from lib import syndicate
from lib.url_signing import new_signed_url


def save_file_obj(dest_path, file_obj, container, syndicate_name, content_type):
    fqp = path.join(settings.MEDIA_ROOT, container, dest_path)
    if not path.exists(path.dirname(fqp)):
        os.makedirs(path.dirname(fqp))

    with open(fqp, 'wb+') as dest_file:
        copyfileobj(file_obj, dest_file)

    uri = '{}{}/{}'.format(settings.MEDIA_URL, container, dest_path)
    internal_url = new_signed_url(settings.INTERNAL_MEDIA_HOST + uri)
    external_url = new_signed_url(syndicate.build_full_url_for_syndicate(uri, syndicate_name))
    return internal_url, external_url

def list_dir(dir_path, container):
    fqp = path.join(settings.MEDIA_ROOT, container, dir_path)
    return [ path.join(path.normpath(dir_path), f) for f in os.listdir(fqp) ]

def retrieve_to_file_obj(src_path, file_obj, container):
    fqp = path.join(settings.MEDIA_ROOT, container, src_path)
    if not path.isfile(fqp):
        return
    with open(fqp, 'rb') as src_file:
        copyfileobj(src_file, file_obj)

def delete_dir(dir_path, container):
    fqp = path.join(settings.MEDIA_ROOT, container, dir_path)
    rmtree(fqp, ignore_errors=True)

def delete_file(file_path, container):
    fqp = path.join(settings.MEDIA_ROOT, container, file_path)
    os.remove(fqp)
