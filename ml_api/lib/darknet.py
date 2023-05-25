# pylint: disable=R, W0401, W0614, W0703
from ctypes import *
import random
import os
import cv2
import platform
from typing import List, Tuple

# C-structures from Darknet lib

class BOX(Structure):
    _fields_ = [("x", c_float),
                ("y", c_float),
                ("w", c_float),
                ("h", c_float)]


class DETECTION(Structure):
    _fields_ = [("bbox", BOX),
                ("classes", c_int),
                ("best_class_idx", c_int),
                ("prob", POINTER(c_float)),
                ("mask", POINTER(c_float)),
                ("objectness", c_float),
                ("sort_class", c_int),
                ("uc", POINTER(c_float)),
                ("points", c_int),
                ("embeddings", POINTER(c_float)),
                ("embedding_size", c_int),
                ("sim", c_float),
                ("track_id", c_int)]

class IMAGE(Structure):
    _fields_ = [("w", c_int),
                ("h", c_int),
                ("c", c_int),
                ("data", POINTER(c_float))]


class METADATA(Structure):
    _fields_ = [("classes", c_int),
                ("names", POINTER(c_char_p))]

class YoloNet:
    """Darknet-based detector implementation"""
    net: c_void_p
    meta: METADATA

    def __init__(self, weight_path: str, meta_path: str, config_path: str, asked_to_use_gpu: bool):
        if not os.path.exists(config_path):
            raise ValueError("Invalid config path `"+os.path.abspath(config_path)+"`")
        if not os.path.exists(weight_path):
            raise ValueError("Invalid weight path `"+os.path.abspath(weight_path)+"`")
        if not os.path.exists(meta_path):
            raise ValueError("Invalid data file path `"+os.path.abspath(meta_path)+"`")
        if not lib:
            raise ImportError(f"Unable to load darknet module.")

        if asked_to_use_gpu and not using_gpu:
            raise Exception('I respectfully decline to load the net as I am asked to use GPU but the loaded darknet module does NOT have GPU support')

        self.net = load_net_custom(config_path.encode("ascii"), weight_path.encode("ascii"), 0, 1)  # batch size = 1
        self.meta = load_meta(meta_path.encode("ascii"))

    def detect(self, meta, image, alt_names, thresh=.5, hier_thresh=.5, nms=.45, debug=False) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
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
        predict_image(self.net, im)
        if debug:
            print("did prediction")
        dets = get_network_boxes(self.net, custom_image.shape[1], custom_image.shape[0], thresh, hier_thresh, None, 0, pnum, 0)  # OpenCV
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

# Loads darknet shared library. May fail if some dependencies like OpenCV not installed
# libdarknet_gpu.so needs Cuda + Cudnn and other libraries in path, which may not exist
# For the such case, it will try to load libdarknet.so instead
lib = None
using_gpu = False

print('\n')
try:
    so_path = os.path.join('/darknet', "libdarknet_gpu.so")
    print(f"Let's try darknet lib built with GPU support - {so_path}")
    lib = CDLL(so_path, RTLD_GLOBAL)
    print(f"Done! Hooray! Now we have darknet with GPU support.")
    using_gpu = True

except Exception as e:
    print(f"Nope! Failed to load darknet lib built with GPU support. erors={e}")

    so_path = os.path.join('/darknet', "libdarknet_cpu.so")
    print(f"Now let's try darknet lib on CPU - {so_path}")
    lib = CDLL(so_path, RTLD_GLOBAL)
    print(f"Done! Darknet is now running on CPU.")

print('\n')

if lib:
    lib.network_width.argtypes = [c_void_p]
    lib.network_width.restype = c_int
    lib.network_height.argtypes = [c_void_p]
    lib.network_height.restype = c_int

    predict = lib.network_predict
    predict.argtypes = [c_void_p, POINTER(c_float)]
    predict.restype = POINTER(c_float)

    if using_gpu:
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
    global alt_names

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




