import flask
from flask import request, jsonify
from os import path
import urllib
import cv2
import numpy as np

from lib.prediction_model import load_net, detect

app = flask.Flask(__name__)
app.config['DEBUG'] = True

model_dir = path.join(path.dirname(path.realpath(__file__)), 'model')
net_main, meta_main = load_net(path.join(model_dir, 'model.cfg'), path.join(model_dir, 'model.weights'), path.join(model_dir, 'model.meta'))

@app.route('/predict', methods=['GET'])
def predict():
    if 'img' in request.args:
        resp = urllib.request.urlopen(request.args['img'])
        img_array = np.array(bytearray(resp.read()), dtype=np.uint8)
        img = cv2.imdecode(img_array, -1)
        print("starting")
        result = detect(net_main, meta_main, img, thresh=0.25)
        print(result)
        return jsonify(result)
    else:
        return jsonify([])

app.run(host='0.0.0.0', port=3333, threaded=False)
