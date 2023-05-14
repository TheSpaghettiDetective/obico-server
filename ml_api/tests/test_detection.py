from typing import List, Tuple
import unittest
from lib.detection_model import *
import os
import json
from lib.geometry import Detection, compare_detections
import cv2

TEST_DATA_DIR = "test_data"
DET_THRESHOLD = 0.25
NMS_THRESHOLD = 0.4

def find_images() -> List[Tuple[str, List[Detection]]]:
    res = []
    for name in os.listdir(TEST_DATA_DIR):
        if name.endswith(".jpg"):
            json_path = os.path.join(TEST_DATA_DIR, name[:-3] + "json")
            if os.path.exists(json_path):
                with open(json_path) as f:
                    items = json.load(f)
                    res.append((os.path.join(TEST_DATA_DIR, name), [Detection.from_dict(d) for d in items]))
    return res


class TestDetection(unittest.TestCase):
    def test_darknet(self):
        net, meta = load_net("model/model.cfg", "model/model.weights", "model/model.meta")
        for img_path, detections in find_images():
            custom_image_bgr = cv2.imread(img_path)  
            detected = detect(net, meta, custom_image_bgr, thresh=DET_THRESHOLD, nms=NMS_THRESHOLD)
            detected_detections = Detection.from_tuple_list(detected)
            self.assertTrue(len(detected_detections) > 0)
            similar = compare_detections(detected_detections, detections)
            self.assertTrue(similar)

    def test_onnx(self):
        net, meta = load_net("model/model.cfg", "model/model.onnx", "model/model.meta")
        for img_path, detections in find_images():
            custom_image_bgr = cv2.imread(img_path)  
            detected = detect(net, meta, custom_image_bgr, thresh=DET_THRESHOLD, nms=NMS_THRESHOLD)
            detected_detections = Detection.from_tuple_list(detected)
            self.assertTrue(len(detected_detections) > 0)
            similar = compare_detections(detected_detections, detections)
            self.assertTrue(similar)

