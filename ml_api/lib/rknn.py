from typing import List, Tuple
import numpy as np
import cv2

from lib.meta import Meta
from rknnlite.api import RKNNLite


class RknnNet:
    rknn: RKNNLite
    meta: Meta
    input_h: int
    input_w: int

    def __init__(self, rknn_path: str, meta_path: str, use_gpu: bool):
        self.rknn = RKNNLite()
        ret = self.rknn.load_rknn(rknn_path)
        if ret != 0:
            raise Exception(f'Failed to load RKNN model: {rknn_path} (error code {ret})')

        ret = self.rknn.init_runtime()
        if ret != 0:
            raise Exception(f'Failed to init RKNN runtime (error code {ret})')

        self.meta = Meta(meta_path)
        self.input_h = 416
        self.input_w = 416

    def detect(self, meta, image, alt_names, thresh=.5, hier_thresh=.5, nms=.45, debug=False) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        width = image.shape[1]
        height = image.shape[0]

        # Preprocess input
        resized = cv2.resize(image, (self.input_w, self.input_h), interpolation=cv2.INTER_LINEAR)
        img_in = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        img_in = np.expand_dims(img_in, axis=0)

        # Run inference
        outputs = self.rknn.inference(inputs=[img_in])

        # Dequantize outputs if needed (INT8 model)
        outputs = _dequantize_outputs(outputs)

        detections = post_processing(outputs, width, height, thresh, nms, meta.names)
        return detections[0]

    def __del__(self):
        if hasattr(self, 'rknn') and self.rknn is not None:
            self.rknn.release()


def _dequantize_outputs(outputs):
    dequantized = []
    for out in outputs:
        arr = np.array(out, dtype=np.float32)
        dequantized.append(arr)
    return dequantized


def nms_cpu(boxes, confs, nms_thresh=0.5, min_mode=False):
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
