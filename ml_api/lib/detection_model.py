#!python3

# pylint: disable=R, W0401, W0614, W0703
from ctypes import *
import math
import random
import os
import sys
import cv2
import platform
import time
import argparse

# optional import for onnx
try:
    import onnxruntime
    import numpy as np
    have_onnx = True
except:
    have_onnx = False

def sample(probs):
    s = sum(probs)
    probs = [a/s for a in probs]
    r = random.uniform(0, 1)
    for i in range(len(probs)):
        r = r - probs[i]
        if r <= 0:
            return i
    return len(probs)-1


def c_array(ctype, values):
    arr = (ctype*len(values))()
    arr[:] = values
    return arr


class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]


class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int)]


class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]


class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]


DIRNAME = os.path.abspath(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "bin")
)

hasGPU = os.environ.get('HAS_GPU', 'False') == 'True'
so_path = os.path.join(DIRNAME, "model_{}{}.so".format('gpu_' if hasGPU else '', platform.machine()))

lib = CDLL(so_path, RTLD_GLOBAL)
lib.network_width.argtypes = [c_void_p]
lib.network_width.restype = c_int
lib.network_height.argtypes = [c_void_p]
lib.network_height.restype = c_int

predict = lib.network_predict
predict.argtypes = [c_void_p, POINTER(c_float)]
predict.restype = POINTER(c_float)

if hasGPU:
    set_gpu = lib.cuda_set_device
    set_gpu.argtypes = [c_int]

make_image = lib.make_image
make_image.argtypes = [c_int, c_int, c_int]
make_image.restype = IMAGE

get_network_boxes = lib.get_network_boxes
get_network_boxes.argtypes = [c_void_p, c_int, c_int, c_float, c_float, POINTER(c_int), c_int, POINTER(c_int), c_int]
get_network_boxes.restype = POINTER(DETECTION)

make_network_boxes = lib.make_network_boxes
make_network_boxes.argtypes = [c_void_p]
make_network_boxes.restype = POINTER(DETECTION)

free_detections = lib.free_detections
free_detections.argtypes = [POINTER(DETECTION), c_int]

free_ptrs = lib.free_ptrs
free_ptrs.argtypes = [POINTER(c_void_p), c_int]

network_predict = lib.network_predict
network_predict.argtypes = [c_void_p, POINTER(c_float)]

reset_rnn = lib.reset_rnn
reset_rnn.argtypes = [c_void_p]

load_net = lib.load_network
load_net.argtypes = [c_char_p, c_char_p, c_int]
load_net.restype = c_void_p

load_net_custom = lib.load_network_custom
load_net_custom.argtypes = [c_char_p, c_char_p, c_int, c_int]
load_net_custom.restype = c_void_p

do_nms_obj = lib.do_nms_obj
do_nms_obj.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

do_nms_sort = lib.do_nms_sort
do_nms_sort.argtypes = [POINTER(DETECTION), c_int, c_int, c_float]

free_image = lib.free_image
free_image.argtypes = [IMAGE]

letterbox_image = lib.letterbox_image
letterbox_image.argtypes = [IMAGE, c_int, c_int]
letterbox_image.restype = IMAGE

load_meta = lib.get_metadata
lib.get_metadata.argtypes = [c_char_p]
lib.get_metadata.restype = METADATA

load_image = lib.load_image_color
load_image.argtypes = [c_char_p, c_int, c_int]
load_image.restype = IMAGE

rgbgr_image = lib.rgbgr_image
rgbgr_image.argtypes = [IMAGE]

predict_image = lib.network_predict_image
predict_image.argtypes = [c_void_p, IMAGE]
predict_image.restype = POINTER(c_float)


def array_to_image(arr):
    import numpy as np
    # need to return old values to avoid python freeing memory
    arr = arr.transpose(2, 0, 1)
    c = arr.shape[0]
    h = arr.shape[1]
    w = arr.shape[2]
    arr = np.ascontiguousarray(arr.flat, dtype=np.float32) / 255.0
    data = arr.ctypes.data_as(POINTER(c_float))
    im = IMAGE(w, h, c, data)
    return im, arr


def classify(net, meta, im):
    out = predict_image(net, im)
    res = []
    for i in range(meta.classes):
        if alt_names is None:
            nameTag = meta.names[i]
        else:
            nameTag = alt_names[i]
        res.append((nameTag, out[i]))
    res = sorted(res, key=lambda x: -x[1])
    return res


def detect(net, meta, image, thresh=.5, hier_thresh=.5, nms=.45, debug=False):
    if have_onnx and isinstance(net, onnxruntime.InferenceSession):
        return detect_onnx(net, meta, image, thresh, nms)
    #pylint: disable= C0321
    custom_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    im, arr = array_to_image(custom_image)             # you should comment line below: free_image(im)
    if debug:
        print("Loaded image")
    num = c_int(0)
    if debug:
        print("Assigned num")
    pnum = pointer(num)
    if debug:
        print("Assigned pnum")
    predict_image(net, im)
    if debug:
        print("did prediction")
    dets = get_network_boxes(net, custom_image.shape[1], custom_image.shape[0], thresh, hier_thresh, None, 0, pnum, 0)  # OpenCV
    if debug:
        print("Got dets")
    num = pnum[0]
    if debug:
        print("got zeroth index of pnum")
    if nms:
        do_nms_sort(dets, num, meta.classes, nms)
    if debug:
        print("did sort")
    res = []
    if debug:
        print("about to range")
    for j in range(num):
        if debug:
            print("Ranging on "+str(j)+" of "+str(num))
        if debug:
            print("Classes: "+str(meta), meta.classes, meta.names)
        for i in range(meta.classes):
            if debug:
                print("Class-ranging on "+str(i)+" of "+str(meta.classes)+"= "+str(dets[j].prob[i]))
            if dets[j].prob[i] > 0:
                b = dets[j].bbox
                if alt_names is None:
                    nameTag = meta.names[i]
                else:
                    nameTag = alt_names[i]
                if debug:
                    print("Got bbox", b)
                    print(nameTag)
                    print(dets[j].prob[i])
                    print((b.x, b.y, b.w, b.h))
                res.append((nameTag, dets[j].prob[i], (b.x, b.y, b.w, b.h)))
    if debug:
        print("did range")
    res = sorted(res, key=lambda x: -x[1])
    if debug:
        print("did sort")
    free_detections(dets, num)
    if debug:
        print("freed detections")
    return res

def nms_cpu(boxes, confs, nms_thresh=0.5, min_mode=False):
    # print(boxes.shape)
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    areas = (x2 - x1) * (y2 - y1)
    order = confs.argsort()[::-1]

    keep = []
    while order.size > 0:
        idx_self = order[0]
        idx_other = order[1:]

        keep.append(idx_self)

        xx1 = np.maximum(x1[idx_self], x1[idx_other])
        yy1 = np.maximum(y1[idx_self], y1[idx_other])
        xx2 = np.minimum(x2[idx_self], x2[idx_other])
        yy2 = np.minimum(y2[idx_self], y2[idx_other])

        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        inter = w * h

        if min_mode:
            over = inter / np.minimum(areas[order[0]], areas[order[1:]])
        else:
            over = inter / (areas[order[0]] + areas[order[1:]] - inter)

        inds = np.where(over <= nms_thresh)[0]
        order = order[inds + 1]
    
    return np.array(keep)

def post_processing(output, width, height, conf_thresh, nms_thresh, names):
    box_array = output[0]
    confs = output[1]

    if type(box_array).__name__ != 'ndarray':
        box_array = box_array.cpu().detach().numpy()
        confs = confs.cpu().detach().numpy()

    num_classes = confs.shape[2]

    # [batch, num, 4]
    box_array = box_array[:, :, 0]

    # [batch, num, num_classes] --> [batch, num]
    max_conf = np.max(confs, axis=2)
    max_id = np.argmax(confs, axis=2)

    box_x1x1x2y2_to_xcycwh_scaled = lambda b: \
        (
            0.5 * width * (b[0] + b[2]), 
            0.5 * height * (b[1] + b[3]), 
            width * (b[2] - b[0]),
            width * (b[3] - b[1])
         )
    dets_batch = []
    for i in range(box_array.shape[0]):
       
        argwhere = max_conf[i] > conf_thresh
        l_box_array = box_array[i, argwhere, :]
        l_max_conf = max_conf[i, argwhere]
        l_max_id = max_id[i, argwhere]

        bboxes = []
        # nms for each class
        for j in range(num_classes):

            cls_argwhere = l_max_id == j
            ll_box_array = l_box_array[cls_argwhere, :]
            ll_max_conf = l_max_conf[cls_argwhere]
            ll_max_id = l_max_id[cls_argwhere]

            keep = nms_cpu(ll_box_array, ll_max_conf, nms_thresh)
            
            if (keep.size > 0):
                ll_box_array = ll_box_array[keep, :]
                ll_max_conf = ll_max_conf[keep]
                ll_max_id = ll_max_id[keep]

                for k in range(ll_box_array.shape[0]):
                    bboxes.append([ll_box_array[k, 0], ll_box_array[k, 1], ll_box_array[k, 2], ll_box_array[k, 3], ll_max_conf[k], ll_max_conf[k], ll_max_id[k]])
        
        detections = [(names[b[6]], b[4], box_x1x1x2y2_to_xcycwh_scaled((b[0], b[1], b[2], b[3]))) for b in bboxes]
        dets_batch.append(detections)

    
    return dets_batch


def detect_onnx(session, meta, image, thresh, nms_thresh):
    input_h = session.get_inputs()[0].shape[2]
    input_w = session.get_inputs()[0].shape[3]
    width = image.shape[1]
    height = image.shape[0]

    # Input
    resized = cv2.resize(image, (input_w, input_h), interpolation=cv2.INTER_LINEAR)
    img_in = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    img_in = np.transpose(img_in, (2, 0, 1)).astype(np.float32)
    img_in = np.expand_dims(img_in, axis=0)
    img_in /= 255.0

    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: img_in})

    detections = post_processing(outputs, width, height, thresh, nms_thresh, alt_names or meta.names)
    return detections 


net_main = None
meta_main = None
alt_names = None


def load_net_onnx(onnx_path: str):
    session = onnxruntime.InferenceSession(onnx_path)
    return session


def load_net(config_path, weight_path, meta_path):
    global meta_main, net_main, alt_names  # pylint: disable=W0603
    if not os.path.exists(config_path):
        raise ValueError("Invalid config path `"+os.path.abspath(config_path)+"`")
    if not os.path.exists(weight_path):
        raise ValueError("Invalid weight path `"+os.path.abspath(weight_path)+"`")
    if not os.path.exists(meta_path):
        raise ValueError("Invalid data file path `"+os.path.abspath(meta_path)+"`")
    if net_main is None:
        if have_onnx and weight_path.endswith(".onnx"):
            net_main = load_net_onnx(weight_path)
        else:
            net_main = load_net_custom(config_path.encode("ascii"), weight_path.encode("ascii"), 0, 1)  # batch size = 1
    if meta_main is None:
        meta_main = load_meta(meta_path.encode("ascii"))
    if alt_names is None:
        # In Python 3, the metafile default access craps out on Windows (but not Linux)
        # Read the names file and create a list to feed to detect
        try:
            with open(meta_path) as metaFH:
                metaContents = metaFH.read()
                import re
                match = re.search("names *= *(.*)$", metaContents, re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1)
                else:
                    result = None
                try:
                    if os.path.exists(result):
                        with open(result) as namesFH:
                            namesList = namesFH.read().strip().split("\n")
                            alt_names = [x.strip() for x in namesList]
                except TypeError:
                    pass
        except Exception:
            pass

    return net_main, meta_main


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=str, help="Image file path")
    parser.add_argument("--weights", type=str, default="model/model.weights", help="Model weights file")
    parser.add_argument("--det-threshold", type=float, default=0.25, help="Detection threshold")
    parser.add_argument("--nms-threshold", type=float, default=0.4, help="NMS threshold")
    parser.add_argument("--preheat", action='store_true', help="Make a dry run of NN for initlalization")
    parser.add_argument("--cpu", action='store_true', help="Force use CPU")
    opt = parser.parse_args()

    net_main_1, meta_main_1 = load_net("model/model.cfg", opt.weights, "model/model.meta")

    # force use CPU, only implemented for ONNX
    if opt.cpu and have_onnx and isinstance(net_main_1, onnxruntime.InferenceSession):
        net_main_1.set_providers(['CPUExecutionProvider'])

    import cv2
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

    print(detections)
