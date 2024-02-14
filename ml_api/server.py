#!/usr/bin/env python

import flask
from flask import abort, make_response, request, jsonify
from os import path, environ
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
import cv2
import numpy as np
import requests

from auth import token_required
from lib.detection_model import load_net, detect

# connection timeouts for python.requests for connect/read, bump it for slow endpoints
# especially if using esp32 cameras directly
TIMEOUT_CONNECT = float(environ.get("TIMEOUT_CONNECT", "0.1"))
TIMEOUT_READ = float(environ.get("TIMEOUT_READ", "5"))
# The threshold for a box to be considered a positive detection
THRESH = float(environ.get("THRESH", "0.08"))
SESSION_TTL_SECONDS = float(environ.get("SESSION_TTL_SECONDS", 60 * 2))
app = flask.Flask(__name__)

# Sentry
if environ.get("SENTRY_DSN"):
    app.logger.info(f"SENTRY_DSN=***masked***")
    sentry_sdk.init(
        dsn=environ.get("SENTRY_DSN"),
        integrations=[
            FlaskIntegration(),
        ],
    )

status = dict()

# SECURITY WARNING: don't run with debug turned on in production!
app.config["DEBUG"] = environ.get("DEBUG") == "True"

app.logger.info(f"DEBUG={app.config['DEBUG']}")
app.logger.info(f"SESSION_TTL_SECONDS={SESSION_TTL_SECONDS}")
app.logger.info(f"THRESH={THRESH}")
app.logger.info(f"TIMEOUT_CONNECT={TIMEOUT_CONNECT}")
app.logger.info(f"TIMEOUT_READ={TIMEOUT_READ}")

# load ai/ml models
model_dir = path.join(path.dirname(path.realpath(__file__)), "model")
net_main = load_net(
    path.join(model_dir, "model.cfg"), path.join(model_dir, "model.meta")
)


# process detection of the image, pass 'img' as param
@app.route("/p/", methods=["GET"])
@token_required
def get_p():
    if "img" in request.args:
        try:
            resp = requests.get(
                request.args["img"],
                stream=True,
                timeout=(TIMEOUT_CONNECT, TIMEOUT_READ),
            )
            resp.raise_for_status()
            img_array = np.array(bytearray(resp.content), dtype=np.uint8)
            img = cv2.imdecode(img_array, -1)
            detections = detect(net_main, img, thresh=THRESH)
            return jsonify({"detections": detections})
        except Exception as err:
            sentry_sdk.capture_exception()
            app.logger.error(f"Failed to get image {request.args} - {err}")
            abort(
                make_response(
                    jsonify(
                        detections=[],
                        message=f"Failed to get image {request.args} - {err}",
                    ),
                    503,
                )
            )

    else:
        app.logger.warn(f"Invalid request params: {request.args}")
        abort(
            make_response(
                jsonify(
                    detections=[], message=f"Invalid request params: {request.args}"
                ),
                400,
            )
        )


# healtchcheck and readiness endpoint
@app.route("/hc/", methods=["GET"])
def health_check():
    return "ok" if net_main is not None else "error"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3333, threaded=False)
