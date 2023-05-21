from typing import List, Tuple
import onnxruntime
import numpy as np
import cv2
import os
import logging

from lib.meta import Meta

has_GPU = os.environ.get('HAS_GPU', 'False').lower() in ('true', '1', 'yes', 'on')
ONNX_NUM_THREADS = int(os.environ.get('ONNX_NUM_THREADS', '1'))

class OnnxNet:
    session: onnxruntime.InferenceSession
    meta: Meta
    has_gpu: bool

    def __init__(self, onnx_path: str, meta_path: str):
        global has_GPU

        if not os.path.exists(onnx_path):
            raise ValueError("Invalid weight path `"+os.path.abspath(onnx_path)+"`")
        if not os.path.exists(meta_path):
            raise ValueError("Invalid data file path `"+os.path.abspath(meta_path)+"`")
        providers = ['CUDAExecutionProvider'] if has_GPU else ['CPUExecutionProvider']

        sess_options = None
        if not has_GPU and ONNX_NUM_THREADS > 0:
            sess_options = onnxruntime.SessionOptions()
            sess_options.intra_op_num_threads = ONNX_NUM_THREADS 
            sess_options.execution_mode = onnxruntime.ExecutionMode.ORT_SEQUENTIAL
            sess_options.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL

        try:
            logging.warning(f'Trying to load ONNX from {onnx_path} - options: {sess_options} - providers: {providers}')
            self.session = onnxruntime.InferenceSession(onnx_path, sess_options, providers=providers)
        except Exception as e:
            logging.warning(f"Unable to create ONNX session. HAS_GPU={has_GPU}, error={e}")
            if has_GPU:
                print("Trying to fallback into CPU execution")
                has_GPU = False
                sess_options = None
                if ONNX_NUM_THREADS > 0:
                    sess_options = onnxruntime.SessionOptions()
                    sess_options.intra_op_num_threads = ONNX_NUM_THREADS 
                    sess_options.execution_mode = onnxruntime.ExecutionMode.ORT_SEQUENTIAL
                    sess_options.graph_optimization_level = onnxruntime.GraphOptimizationLevel.ORT_ENABLE_ALL
                providers = ['CPUExecutionProvider']
                self.session = onnxruntime.InferenceSession(onnx_path, sess_options, providers=providers)

        self.meta = Meta(meta_path)
        self.has_gpu = has_GPU

    def get_runtime_type(self) -> str:
        return "ONNX"

    def has_gpu_enabled(self) -> bool:
        return self.has_gpu

    def detect(self, meta, image, alt_names, thresh=.5, hier_thresh=.5, nms=.45, debug=False) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        input_h = self.session.get_inputs()[0].shape[2]
        input_w = self.session.get_inputs()[0].shape[3]
        width = image.shape[1]
        height = image.shape[0]

        # Input
        resized = cv2.resize(image, (input_w, input_h), interpolation=cv2.INTER_LINEAR)
        img_in = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        img_in = np.transpose(img_in, (2, 0, 1)).astype(np.float32)
        img_in = np.expand_dims(img_in, axis=0)
        img_in /= 255.0

        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: img_in})

        detections = post_processing(outputs, width, height, thresh, nms, meta.names)
        return detections[0]

    def force_cpu(self):
        self.session.set_providers(['CPUExecutionProvider'])

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
            float(0.5 * width * (b[0] + b[2])), 
            float(0.5 * height * (b[1] + b[3])), 
            float(width * (b[2] - b[0])),
            float(width * (b[3] - b[1]))
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
        
        detections = [(names[b[6]], float(b[4]), box_x1x1x2y2_to_xcycwh_scaled((b[0], b[1], b[2], b[3]))) for b in bboxes]
        dets_batch.append(detections)

    
    return dets_batch



