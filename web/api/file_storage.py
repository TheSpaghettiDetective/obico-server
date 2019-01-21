from datetime import datetime, timedelta
from django.conf import settings
import os
from azure.storage.blob import BlockBlobService, BlobPermissions

def save_file_obj(dest_path, file_obj, request):
    if settings.AZURE_STORAGE_CONNECTION_STRING:
        return _save_to_azure(dest_path, file_obj)
    else:
        return _save_to_file_system(dest_path, file_obj, request)

def _save_to_file_system(dest_path, file_obj, request):
    fqp = os.path.join(settings.MEDIA_ROOT, dest_path)
    if not os.path.exists(os.path.dirname(fqp)):
        os.makedirs(os.path.dirname(fqp))

    with open(fqp, 'wb+') as dest_file:
        for chunk in file_obj.chunks():
            dest_file.write(chunk)

    uri = settings.MEDIA_URL + dest_path
    if settings.EXTERNAL_MEDIA_HOST:
        external_url = settings.EXTERNAL_MEDIA_HOST + uri
    else:
        external_url = request.build_absolute_uri(uri)

    return settings.INTERNAL_MEDIA_HOST + uri, external_url

def _save_to_azure(dest_path, file_obj):
    blob_service = BlockBlobService(connection_string=settings.AZURE_STORAGE_CONNECTION_STRING)

    container = settings.AZURE_STORAGE_CONTAINER
    blob_service.create_blob_from_stream(container, dest_path, file_obj)
    sas_token = blob_service.generate_blob_shared_access_signature(
        container,
        dest_path,
        BlobPermissions.READ,datetime.utcnow() + timedelta(hours=24*3000))
    return blob_service.make_blob_url(container, dest_path, sas_token=sas_token)