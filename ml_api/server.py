#!/usr/bin/env python

import flask
from flask import request, jsonify
from os import path, environ
from raven.contrib.flask import Sentry
import cv2
import numpy as np

from auth import token_required
from lib.detection_model import load_net, detect
from lib.retry import request_with_retry

SESSION_TTL_SECONDS = 60*2

app = flask.Flask(__name__)

# SECURITY WARNING: don't run with debug turned on in production!
app.config['DEBUG'] = environ.get('DEBUG') == 'True'

# Sentry
if environ.get('SENTRY_DSN'):
    sentry = Sentry(app, dsn=environ.get('SENTRY_DSN'))

model_dir = path.join(path.dirname(path.realpath(__file__)), 'model')
net_main, meta_main = load_net(path.join(model_dir, 'model.cfg'), path.join(model_dir, 'model.weights'), path.join(model_dir, 'model.meta'))

@app.route('/p/', methods=['GET'])
@token_required
def get_p():
    if 'img' in request.args:
        resp = request_with_retry(request.args['img'])
        img_array = np.array(bytearray(resp.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)
        detections = detect(net_main, meta_main, img, thresh=0.25)
        return jsonify({'detections': detections})

    else:
        app.logger.warn("Invalid request params: {}".format(request.args))
        return jsonify([])

app.run(host='0.0.0.0', port=3333, threaded=False)
