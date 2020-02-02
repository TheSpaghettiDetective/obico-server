#!/usr/bin/env python

import flask
from flask import request, jsonify, Response, send_file
from os import path, environ
from raven.contrib.flask import Sentry
import cv2
import numpy as np
import requests
import json
import logging
from datetime import datetime
from auth import token_required
from lib.detection_model import load_net, detect
#import ptvsd
from io import BytesIO
from PIL import Image

THRESH = 0.08  # The threshold for a box to be considered a positive detection
SESSION_TTL_SECONDS = 60*2

app = flask.Flask(__name__)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.info')
    app.logger.handlers.extend(gunicorn_logger.handlers)
    # setup remote debugger
    # ptvsd.enable_attach(address = ('0.0.0.0', 3002), redirect_output=True)

# SECURITY WARNING: don't run with debug turned on in production!
app.config['DEBUG'] = (environ.get('DEBUG') == 'True')

#debug_func = app.logger.info if app.config['DEBUG'] else None

# Sentry
sentry = None
if environ.get('SENTRY_DSN'):
    sentry = Sentry(app, dsn=environ.get('SENTRY_DSN'))

# get model, and settings from env
model_xml = environ.get("MODEL_XML", None)
if model_xml is None:
    model_xml = path.join(path.join(path.dirname(path.realpath(__file__)), 'model'), 'model.xml')

model_labels  = environ.get("MODEL_LABELS", None)
if model_labels is None:
    model_labels = path.join(path.join(path.dirname(path.realpath(__file__)), 'model'), 'model.labels')

device  = environ.get("OPENVINO_DEVICE", "CPU")
cpu_extension  = environ.get("OPENVINO_CPU_EXTENSION", None)

model = load_net(model_xml, model_labels, device, cpu_extension, app.logger)

@app.route('/p/', methods=['GET'])
#@token_required
def get_p():
    if 'img' in request.args:
        try:
            show = 'show' in request.args
            url = request.args['img']
            if url.startswith('http'):
                resp = requests.get(url, stream=True, timeout=(0.1, 5))
                resp.raise_for_status()
                img_array = np.array(bytearray(resp.content), dtype=np.uint8)
            else:
                img_path = path.join(path.dirname(path.realpath(__file__)), url)
                app.logger.info('path %s' % img_path)
                with open(img_path, 'rb') as infile:
                    buf = infile.read()
                img_array = np.fromstring(buf, dtype='uint8')

            img = cv2.imdecode(img_array, -1)
            start = datetime.now()
            result = detect(model, img, thresh=THRESH, show=show)
            if show:
                img = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(img)
                img2 = BytesIO()
                img.save(img2, format="jpeg")
                img2.seek(0)
                return send_file(img2, mimetype='image/jpeg')
            else:
                timetaken = datetime.now() - start
                app.logger.info("INFERENCE: %s" % timetaken)
                result = {'time-taken': str(timetaken),'detections': result}
                if len(result) > 0:
                    app.logger.info(json.dumps(result))
                return jsonify(result)

        except Exception as ex:
            if sentry:
                sentry.captureException()
            return jsonify({'detections':[], 'error': ex.__str__})
    else:
        app.logger.warn("Invalid request params: {}".format(request.args))

    return jsonify({'detections': []})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3333, threaded=False)
