import logging
import os
import re

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError, Http404

from app import models
from config import settings
from lib.utils import safe_path_join

LOGGER = logging.getLogger(__name__)


def server_media_catchall(request, *args, **kwargs):
    """Catch any media requests that aren't being served through serve_media (help identify legacy requests)"""
    msg = f"UNAUTHENTICATED MEDIA REQUEST - Add a proper media_pattern pointing to the server_media() view: {request.path}"
    LOGGER.error(msg)
    return HttpResponseServerError(msg)


def serve_media(request, file_name, printer_id=None, print_id=None, user_id=None, **kwargs):
    """
    Serves media files while enforcing permissions based on given object IDs.

    Must supply at least one of:
        - printer_id
        - print_id
        - user_id
    """
    # Strip /media/ from beginning of path
    relative_media_path = request.path.replace(settings.MEDIA_URL, '', 1)
    full_path = safe_path_join(settings.MEDIA_ROOT, relative_media_path)
    if not request_is_authorized(request, printer_id=printer_id, print_id=print_id, user_id=user_id):
        return HttpResponseForbidden("You don't have permission to access this media")
    if not os.path.exists(full_path):
        return Http404(f"Requested file does not exist: {full_path}")
    # Serve content based on file_name extension
    filepath_extension = os.path.splitext(file_name)[1]
    content_types = {
        '.mp4': 'video/mp4',
        '.jpg': 'image/jpeg',
        '.gcode': 'text/plain',
        '.json': 'text/plain'
    }
    content_type = content_types.get(filepath_extension.lower(), 'text/plain')
    with open(full_path, 'rb') as fh:
        return HttpResponse(fh, content_type=content_type)


def serve_timelapse_mp4(request, file_name):
    """
    Serves timelapse files and enforces permissions based on filename (print id).
    """
    print_id = int(re.search(r'\d+', file_name).group())  # get print_id from beginning of filename
    return serve_media(request, file_name, print_id=print_id)


def request_is_authorized(
        request: WSGIRequest, printer_id: int = None, print_id: int = None, user_id: int = None
):
    """
    Check if a requst is authorized to access a resource given one (or many) object IDs

    Returns (bool): True if authorized, else False
    """
    if not any([printer_id, print_id, user_id]):
        raise ValueError("Must supply a printer_id, print_id or user_id to perform authc/authz!")
    requesting_user = request.user
    owning_user = []
    if user_id is not None:
        owning_user.append(models.User.objects.get(id=user_id))
    if print_id is not None:
        owning_user.append(models.Print.objects.get(id=print_id).user)
    if printer_id is not None:
        owning_user.append(models.Printer.objects.get(id=printer_id).user)
    # Only return True requesting user matches the owning user for all resources, else False
    return all([user == requesting_user for user in owning_user])
