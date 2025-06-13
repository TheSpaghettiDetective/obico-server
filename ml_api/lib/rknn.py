from typing import List, Tuple
from rknnlite.api import RKNNLite
import numpy as np
import cv2
import os
from typing import Callable
from pathlib import Path

from lib.meta import Meta


class RKNNNet(object):
    # We can't get this at runtime, so we must provide it
    MODEL_INPUT_IMAGE_SIZE = (416, 416)

    def __init__(self, rknn_path: os.PathLike, meta_path: os.PathLike):
        self.__meta = Meta(meta_path)
        self.__rknn = RKNNLite()
        self._checked_call(self.__rknn.load_rknn, str(Path(rknn_path)))
        self._checked_call(self.__rknn.init_runtime)

    def __del__(self):
        self.__rknn.release()

    @property
    def meta(self):
        return self.__meta

    def detect(
        self, meta, image, alt_names, thresh=0.5, hier_thresh=0.5, nms=0.45, debug=False
    ) -> List[Tuple[str, float, Tuple[float, float, float, float]]]:
        return self.post_processing(
            self.__rknn.inference(
                inputs=[self._prepare_image(image)], data_format="nhwc"
            ),
            image.shape[1],  # Width
            image.shape[0],  # Height
            thresh,
            nms,
            meta.names,
        )[0]

    @staticmethod
    def _checked_call(c: Callable, *args, **kwargs):
        rc = c(*args, **kwargs)
        if rc:
            raise RuntimeError(f"{c.__name__} returned {rc}")

    @classmethod
    def _prepare_image(cls, image):
        scaled = cv2.resize(
            image, cls.MODEL_INPUT_IMAGE_SIZE, interpolation=cv2.INTER_LINEAR
        )
        img = cv2.cvtColor(scaled, cv2.COLOR_BGR2RGB)
        # Due to RKNN's internal input transformation, we don't need to normalize here
        # and the model's inputs are quantized to unit8
        # We also don't need to transpose, since RKNN wants NHWC
        img = np.expand_dims(img.astype(np.uint8), 0)
        return img

    @staticmethod
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

    @classmethod
    def post_processing(cls, output, width, height, conf_thresh, nms_thresh, names):
        box_array = output[0]
        confs = output[1]

        if type(box_array).__name__ != "ndarray":
            box_array = box_array.cpu().detach().numpy()
            confs = confs.cpu().detach().numpy()

        num_classes = confs.shape[2]

        # [batch, num, 4]
        box_array = box_array[:, :, 0]

        # [batch, num, num_classes] --> [batch, num]
        max_conf = np.max(confs, axis=2)
        max_id = np.argmax(confs, axis=2)

        box_x1x1x2y2_to_xcycwh_scaled = lambda b: (
            float(0.5 * width * (b[0] + b[2])),
            float(0.5 * height * (b[1] + b[3])),
            float(width * (b[2] - b[0])),
            float(width * (b[3] - b[1])),
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

                keep = cls.nms_cpu(ll_box_array, ll_max_conf, nms_thresh)

                if keep.size > 0:
                    ll_box_array = ll_box_array[keep, :]
                    ll_max_conf = ll_max_conf[keep]
                    ll_max_id = ll_max_id[keep]

                    for k in range(ll_box_array.shape[0]):
                        bboxes.append(
                            [
                                ll_box_array[k, 0],
                                ll_box_array[k, 1],
                                ll_box_array[k, 2],
                                ll_box_array[k, 3],
                                ll_max_conf[k],
                                ll_max_conf[k],
                                ll_max_id[k],
                            ]
                        )

            detections = [
                (
                    names[b[6]],
                    float(b[4]),
                    box_x1x1x2y2_to_xcycwh_scaled((b[0], b[1], b[2], b[3])),
                )
                for b in bboxes
            ]
            dets_batch.append(detections)

        return dets_batch
