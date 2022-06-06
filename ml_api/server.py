#!/usr/bin/env python

import flask
from flask import request, jsonify
from os import path, environ
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import cv2
import numpy as np
import requests
import sys
import os

from auth import token_required

THRESH = 0.08  # The threshold for a box to be considered a positive detection
SESSION_TTL_SECONDS = 60*2

# Sentry
if environ.get('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=environ.get('SENTRY_DSN'),
        integrations=[FlaskIntegration(), ],
    )
else:
    import traceback

app = flask.Flask(__name__)

# SECURITY WARNING: don't run with debug turned on in production!
app.config['DEBUG'] = environ.get('DEBUG') == 'True'
LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
app.logger.setLevel(LOGLEVEL)

# To avoid edits to darknet files, symlink the appropriate CPU / GPU library here before importing darknet
darknet_so_path = '/darknet/libdarknet.gpu.so' if environ.get('HAS_GPU') else '/darknet/libdarknet.cpu.so'
app.logger.info(f'Using darknet lib {darknet_so_path}')
sys.path.append("/darknet")
os.symlink(darknet_so_path, '/darknet/libdarknet.so')
import darknet
from darknet_images import image_detection
model_dir = path.join(path.dirname(path.realpath(__file__)), 'model')
network, class_names, class_colors = darknet.load_network(
        path.join(model_dir, 'model.cfg'),
        path.join(model_dir, 'model.meta'),
        path.join(model_dir, 'model.weights')
    )

@app.route('/p/', methods=['GET'])
@token_required
def get_p():
    if 'img' in request.args:
        try:
            app.logger.debug(f"Fetching {request.args['img']}")
            resp = requests.get(request.args['img'], stream=True, timeout=(0.1, 5))
            resp.raise_for_status()
            app.logger.debug(f"Converting image & detecting")
            img_array = np.array(bytearray(resp.content), dtype=np.uint8)
            img = cv2.imdecode(img_array, -1)
            _, detections = image_detection(img, network, class_names, class_colors, THRESH)
            app.logger.debug(f"{len(detections)} detections: {detections}")
            return jsonify({'detections': detections})
        except:
            if environ.get('SENTRY_DSN'):
                sentry_sdk.captureException()
            else:
                traceback.print_exc()
    else:
        app.logger.warn("Invalid request params: {}".format(request.args))

    return jsonify({'detections': []})

@app.route('/hc/', methods=['GET'])
def health_check():
    return 'ok'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3333, threaded=False)
