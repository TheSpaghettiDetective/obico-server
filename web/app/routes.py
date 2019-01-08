from datetime import datetime, timedelta
from flask import render_template, request, jsonify
from werkzeug import secure_filename
import requests
from azure.storage.blob import BlockBlobService, BlobPermissions

from .detect import next_score
from .models import *
from .schemas import *
from app import db, web_app as wa

@wa.route('/')
@wa.route('/index')
def index():
    return render_template('index.html')


# APIs

account = wa.config['AZURE_STORAGE_ACCOUNT']   # Azure account name
key = wa.config['AZURE_STORAGE_KEY']      # Azure Storage account access key
container = wa.config['AZURE_STORAGE_CONTAINER'] # Container name

blob_service = BlockBlobService(account_name=account, account_key=key)

@wa.route('/dev/status', methods=['POST'])
def update_status():

    def file_printing(octoprint_data):
        printing = False
        flags = octoprint_data.get('state', {}).get('flags', {})
        for flag in ('cancelling', 'paused', 'pausing', 'printing', 'resuming', 'finishing'):
            if flags.get(flag, False):
                printing = True

        file_name = octoprint_data.get('job', {}).get('file', {}).get('name')
        return file_name, printing

    status = request.get_json(force=True)
    file_name, printing = file_printing(status.get('octoprint_data', {}))

    existing_print = db.session.query(Print).filter(Print.printer_id == 2, Print.finished_at == None).first()

    if existing_print and existing_print.name != file_name:
        existing_print.finished_at = datetime.now()
        db.session.commit()
        existing_print = None

    if printing and not existing_print:
        existing_print = Print(name=file_name, printer_id=2, current_img_num=0)
        db.session.add(existing_print)
        db.session.commit()

    return jsonify({'result': 'OK'})

@wa.route('/dev/pic', methods=['POST'])
def detect():
    existing_print = db.session.query(Print).filter(Print.printer_id == 2, Print.finished_at == None).first()

    if not existing_print:
        return jsonify({'result': 'OK'})

    pic = request.files['pic']
    print(pic)

    blob_service.create_blob_from_stream(container, '1.jpg', pic)
    sas_token = blob_service.generate_blob_shared_access_signature(container,'1.jpg',BlobPermissions.READ,datetime.utcnow() + timedelta(hours=24*3000))
    blob_url = blob_service.make_blob_url(container, '1.jpg', sas_token=sas_token)
    resp = requests.get('http://ml_api:3333/p', params={'img': blob_url})
    resp.raise_for_status()

    det = resp.json()
    score = next_score( existing_print.detection_score, det)
    if existing_print:
        existing_print.detection_score = score
        existing_print.current_img_url= blob_url
        existing_print.current_img_num += 1
        db.session.commit()

    print(det)
    print(score)
    return jsonify({'result': det})

@wa.route('/api/prints', methods=['GET'])
def get_prints():
    prints = db.session.query(Print).filter(Print.printer_id == 2, Print.finished_at == None).all()
    return jsonify(PrintSchema(many=True).dump(prints).data)


