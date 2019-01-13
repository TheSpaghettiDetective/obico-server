from datetime import datetime, timedelta
from django.conf import settings
from azure.storage.blob import BlockBlobService, BlobPermissions

def save_file_obj(dest_path, file_obj):
    blob_service = BlockBlobService(connection_string=settings.AZURE_STORAGE_CONNECTION_STRING)

    container = settings.AZURE_STORAGE_CONTAINER
    blob_service.create_blob_from_stream(container, dest_path, file_obj)
    sas_token = blob_service.generate_blob_shared_access_signature(
        container,
        dest_path,
        BlobPermissions.READ,datetime.utcnow() + timedelta(hours=24*3000))
    return blob_service.make_blob_url(container, dest_path, sas_token=sas_token)