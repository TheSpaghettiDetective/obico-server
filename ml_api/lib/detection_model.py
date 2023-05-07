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
    """Loads network from config files and weights. Automatically detects the backend."""
    # nets are loaded only once and then reused
    global meta_main, net_main, alt_names  # pylint: disable=W0603

    if net_main is None:
        if onnx_ready and weight_path.endswith(".onnx"):
            net_main = OnnxNet(weight_path, meta_path)
        elif darknet_ready:
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
    """Runs detection on some image content"""

    return net.detect(meta, image, alt_names, thresh, hier_thresh, nms, debug)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=str, help="Image file path")
    parser.add_argument("--weights", type=str, default="model/model.weights", help="Model weights file")
    parser.add_argument("--det-threshold", type=float, default=0.25, help="Detection threshold")
    parser.add_argument("--nms-threshold", type=float, default=0.4, help="NMS threshold")
    parser.add_argument("--preheat", action='store_true', help="Make a dry run of NN for initlalization")
    parser.add_argument("--cpu", action='store_true', help="Force use CPU")
    parser.add_argument("--save-detections-to", type=str, help="Save detections into this file")
    parser.add_argument("--compare-detections-with", type=str, help="Load detections from this file and compare with result")
    parser.add_argument("--print", action='store_true', help="Print detections")
    opt = parser.parse_args()

    net_main_1, meta_main_1 = load_net("model/model.cfg", opt.weights, "model/model.meta")

    # force use CPU, only implemented for ONNX
    if opt.cpu and onnx_ready and isinstance(net_main_1, OnnxNet):
        net_main_1.set_providers(['CPUExecutionProvider'])

    import cv2
    from dataclasses import asdict
    import json
    from geometry import compare_detections, Detection

    custom_image_bgr = cv2.imread(opt.image)  # use: detect(,,imagePath,)

    # this will make library initialize all the required resources at the first run
    # then the following runs will be much faster
    if opt.preheat:
        detections = detect(net_main_1, meta_main_1, custom_image_bgr, thresh=opt.det_threshold, nms=opt.nms_threshold)

    started_at = time.time()
    detections = detect(net_main_1, meta_main_1, custom_image_bgr, thresh=opt.det_threshold, nms=opt.nms_threshold)
    finished_at = time.time()
    execution_time = finished_at - started_at
    print(f"Execution time: {execution_time:.3} sec")

    detections = Detection.from_tuple_list(detections[0])
    # dump detections into some file
    if opt.save_detections_to:
        with open(opt.save_detections_to, "w") as f:
            json.dump([asdict(d) for d in detections], f)

    # load detections from some file and compare with detection result
    if opt.compare_detections_with:
        with open(opt.compare_detections_with) as f:
            items = json.load(f)
            loaded = [Detection.from_dict(d) for d in items]
            compare_result = compare_detections(loaded, detections)
            if not compare_result:
                print(f"Loaded detections and resulting are different")
                exit(1)

    if opt.print:
        print(detections)
