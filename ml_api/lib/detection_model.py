#!python3

# pylint: disable=R, W0401, W0614, W0703
from enum import Enum
import cv2
import time
import argparse
from lib.meta import Meta


#GLOBALS
net_main = None
meta_main = None
alt_names = None

# optional import for darknet
try:
    from lib.backend_darknet import YoloNet
    darknet_ready = True
except:
    darknet_ready = False

# optional import for onnx
try:
    from lib.backend_onnx import OnnxNet
    onnx_ready = True
except:
    onnx_ready = False


def load_net(config_path, weight_path, meta_path):
    global meta_main, net_main, alt_names  # pylint: disable=W0603

    if net_main is None:
        if onnx_ready and weight_path.endswith(".onnx"):
            net_main = OnnxNet(weight_path, meta_path)
        elif darknet_ready and weight_path.endswith(".darknet"):
            net_main = YoloNet(config_path, weight_path, meta_path)
        else:
            raise Exception(f"Unable to load net. Onnx_ready={onnx_ready}, Darknet_ready={darknet_ready}")

    meta_main = net_main.meta

    assert net_main is not None
    assert meta_main is not None

    if alt_names is None:
        # In Python 3, the metafile default access craps out on Windows (but not Linux)
        # Read the names file and create a list to feed to detect
        try:
            meta = Meta(meta_path)
            alt_names = meta.names
        except Exception:
            pass

    return net_main, meta_main

def detect(net, meta, image, thresh=.5, hier_thresh=.5, nms=.45, debug=False):
    return net.detect(meta, image, alt_names, thresh, hier_thresh, nms, debug)

