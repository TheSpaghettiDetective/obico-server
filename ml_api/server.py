import flask
from flask import request, jsonify
from os import path, environ
from raven.contrib.flask import Sentry
import urllib
import cv2
import numpy as np

from auth import token_required
from lib.detection_model import load_net, detect
from lib.session_agg import predict

SESSION_TTL_SECONDS = 60*2

app = flask.Flask(__name__)

# SECURITY WARNING: don't run with debug turned on in production!
app.config['DEBUG'] = environ.get('DEBUG') == 'True'

# Sentry
if environ.get('SENTRY_DSN'):
    sentry = Sentry(app, dsn=environ.get('SENTRY_DSN'))

# REDIS client
import redis
redis_client = redis.Redis.from_url(environ.get("REDIS_URL"), charset="utf-8", decode_responses=True)

model_dir = path.join(path.dirname(path.realpath(__file__)), 'model')
net_main, meta_main = load_net(path.join(model_dir, 'model.cfg'), path.join(model_dir, 'model.weights'), path.join(model_dir, 'model.meta'))

@app.route('/p', methods=['GET'])
@token_required
def get_p():
    if 'img' in request.args and 'session_id' in request.args:

        resp = urllib.request.urlopen(request.args['img'])
        img_array = np.array(bytearray(resp.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)
        detections = detect(net_main, meta_main, img, thresh=0.25)

        key_name = 'p:' + request.args['session_id']
        p, new_session = predict(detections, redis_client.hgetall(key_name))
        redis_client.hmset(key_name, new_session)
        redis_client.expire(key_name, SESSION_TTL_SECONDS)

        return jsonify({'detections': detections, 'p': p})

    else:
        app.logger.warn("Invalid request params: {}".format(request.args))
        return jsonify([])

app.run(host='0.0.0.0', port=3333, threaded=False)
