#!python3

# pylint: disable=R, W0401, W0614, W0703
from enum import Enum
from lib.meta import Meta
import os

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
    global alt_names  # pylint: disable=W0603

    print(f'Trying to load a workable net... config_path: {config_path} - weight_path: {weight_path} - meta_path: {meta_path}')

    net_main = None
    prefer_onnx = weight_path.endswith(".onnx")
    if prefer_onnx:
        if onnx_ready:
            try:
                print('Trying ONNX module...')
                net_main = OnnxNet(weight_path, meta_path)
                print('Succeeded!')
            except Exception as e:
                error = f"Unable to load ONNX module: {e}"
                print(error)
        else:
            print("Onnx is not ready")

    # if darknet requested or if unable to load the onnx
    if net_main is None:
        if darknet_ready:
            try:
                print('Trying YoloNet...')
                net_main = YoloNet(config_path, weight_path, meta_path)
                print('Succeeded!')
            except Exception as e:
                error = f"Unable to load Darknet module: {e}"
                print(error)
        else:
            print("Darknet is not ready")

    if net_main is None:
        return None

    meta_main = net_main.meta

    if alt_names is None:
        # In Python 3, the metafile default access craps out on Windows (but not Linux)
        # Read the names file and create a list to feed to detect
        try:
            meta = Meta(meta_path)
            alt_names = meta.names
        except Exception:
            pass

    return net_main

def detect(net, image, thresh=.5, hier_thresh=.5, nms=.45, debug=False):
    return net.detect(net.meta, image, alt_names, thresh, hier_thresh, nms, debug)

