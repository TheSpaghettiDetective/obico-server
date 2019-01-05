from datetime import datetime, timedelta
from flask import render_template, request, jsonify
from werkzeug import secure_filename

from azure.storage.blob import BlockBlobService, BlobPermissions

from app import web_app as wa

@wa.route('/')
@wa.route('/index')
def index():
    user = {'username': 'Miguel'}
    return render_template('index.html', title='Home', user=user)


# APIs

account = wa.config['AZURE_STORAGE_ACCOUNT']   # Azure account name
key = wa.config['AZURE_STORAGE_KEY']      # Azure Storage account access key
container = wa.config['AZURE_STORAGE_CONTAINER'] # Container name

blob_service = BlockBlobService(account_name=account, account_key=key)

@wa.route('/dev/cam', methods=['POST'])
def detect_img():
    file = request.files['file']
    blob_service.create_blob_from_stream(container, '1.txt', file)
    sas_token = blob_service.generate_blob_shared_access_signature(container,'1.txt',BlobPermissions.READ,datetime.utcnow() + timedelta(hours=1))
    blob_url = blob_service.make_blob_url(container, '1.txt', sas_token=sas_token)
    return jsonify({'result': blob_url})
