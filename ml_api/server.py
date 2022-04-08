#!/usr/bin/env python

import flask
from flask import request, jsonify
from os import path, environ
from raven.contrib.flask import Sentry
import cv2
import numpy as np
import requests
import sys
import os

from auth import token_required

THRESH = 0.08  # The threshold for a box to be considered a positive detection
SESSION_TTL_SECONDS = 60*2

app = flask.Flask(__name__)

# SECURITY WARNING: don't run with debug turned on in production!
app.config['DEBUG'] = environ.get('DEBUG') == 'True'
LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
app.logger.setLevel(LOGLEVEL)

# Sentry
sentry = None
if environ.get('SENTRY_DSN'):
    sentry = Sentry(app, dsn=environ.get('SENTRY_DSN'))
else:
    import traceback

sys.path.append("/darknet")
import darknet
model_dir = path.join(path.dirname(path.realpath(__file__)), 'model')
network, class_names, class_colors = darknet.load_network(
        path.join(model_dir, 'model.cfg'),
        path.join(model_dir, 'model.meta'),
        path.join(model_dir, 'model.weights')
    )

# Modified from darknet_images.py to accept a cv2 image
def image_detection(image, network, class_names, class_colors, thresh):
    # Darknet doesn't accept numpy images.
    # Create one with image we reuse for each detect
    width = darknet.network_width(network)
    height = darknet.network_height(network)
    darknet_image = darknet.make_image(width, height, 3)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (width, height),
                               interpolation=cv2.INTER_LINEAR)
    darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
    detections = darknet.detect_image(network, class_names, darknet_image, thresh)
    darknet.free_image(darknet_image)
    return detections

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
            detections = image_detection(img, network, class_names, class_colors, THRESH)
            app.logger.debug(f"{len(detections)} detections: {detections}")
            return jsonify({'detections': detections})
        except:
            if sentry:
                sentry.captureException()
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
