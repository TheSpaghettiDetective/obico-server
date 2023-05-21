#!python3
import cv2
from dataclasses import asdict
import json
from lib.geometry import compare_detections, Detection
import os
import argparse
import time
from lib.detection_model import *

KNOWN_IMAGE_EXTENSIONS = ('.jpg', '.png')
KNOWN_VIDEO_EXTENSIONS = ('.mp4', '.avi')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=str, help="Image file path")
    parser.add_argument("--weights", type=str, help="Model weights file")
    parser.add_argument("--det-threshold", type=float, default=0.25, help="Detection threshold")
    parser.add_argument("--nms-threshold", type=float, default=0.4, help="NMS threshold")
    parser.add_argument("--preheat", action='store_true', help="Make a dry run of NN for initlalization")
    parser.add_argument("--cpu", action='store_true', help="Force use CPU")
    parser.add_argument("--save-detections-to", type=str, help="Save detections into this file")
    parser.add_argument("--compare-detections-with", type=str, help="Load detections from this file and compare with result")
    parser.add_argument("--render-to", type=str, help="Save detections into this file or directory")
    parser.add_argument("--print", action='store_true', help="Print detections")
    opt = parser.parse_args()

    net_main_1 = load_net("model/model.cfg", "model/model.meta", weights_path=opt.weights)

    # force use CPU, only implemented for ONNX
    if opt.cpu and onnx_ready and isinstance(net_main_1, OnnxNet):
        net_main_1.force_cpu()

    filename = os.path.basename(opt.image)
    filename, extension = os.path.splitext(filename)

    is_image = extension in KNOWN_IMAGE_EXTENSIONS
    is_video = extension in KNOWN_VIDEO_EXTENSIONS
    frame_number = 0
    vwr = None
    if is_video:
        cap = cv2.VideoCapture(opt.image)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        reading_success, custom_image_bgr = cap.read()
        if opt.render_to:
            fourcc = cv2.VideoWriter_fourcc("m", "p", "4", "v")
            vwr = cv2.VideoWriter(opt.render_to, fourcc, fps, (frame_w, frame_h))
    else:
        cap = None
        fps = 0.0
        custom_image_bgr = cv2.imread(opt.image)
        reading_success = True


    # this will make library initialize all the required resources at the first run
    # then the following runs will be much faster
    if opt.preheat:
        detections = detect(net_main_1, custom_image_bgr, thresh=opt.det_threshold, nms=opt.nms_threshold)

    while reading_success:
        started_at = time.time()
        detections = detect(net_main_1, custom_image_bgr, thresh=opt.det_threshold, nms=opt.nms_threshold)
        finished_at = time.time()
        execution_time = finished_at - started_at
        print(f"Frame #{frame_number} execution time: {execution_time:.3} sec, detection count: {len(detections)}")

        detections = Detection.from_tuple_list(detections)
        # dump detections into some file
        if opt.save_detections_to:
            output_filename, output_extension = os.path.splitext(opt.save_detections_to)
            if is_video and not output_extension and not os.path.exists(opt.save_detections_to):
                os.makedirs(opt.save_detections_to)
            if os.path.isdir(opt.save_detections_to):
                if is_video:
                    output_file_name = f"{filename}#{frame_number:04}.json"
                else:
                    output_file_name = f"{filename}.json"
                output_file_name = os.path.join(opt.save_detections_to, output_file_name)
            else:
                output_file_name = opt.save_detections_to

            with open(output_file_name, "w") as f:
                json.dump([asdict(d) for d in detections], f)

        # load detections from some file and compare with detection result
        if opt.compare_detections_with:
            if is_video:
                read_file_name = os.path.join(opt.compare_detections_with, f"{filename}#{frame_number:04}.json")
            else:
                read_file_name = opt.compare_detections_with

            with open(read_file_name) as f:
                items = json.load(f)
                loaded = [Detection.from_dict(d) for d in items]
                compare_result = compare_detections(loaded, detections)
                if not compare_result:
                    print(f"Frame #{frame_number} loaded detections and resulting are different")
        if opt.render_to:
            for d in detections:
                cv2.rectangle(custom_image_bgr,
                    (int(d.box.left()), int(d.box.top())), (int(d.box.right()), int(d.box.bottom())),
                    (0, 255, 0), 2)
            if vwr:
                vwr.write(custom_image_bgr)
            else:
                cv2.imwrite(opt.render_to, custom_image_bgr)


        if opt.print:
            print(detections)

        if is_image:
            reading_success = False
        elif cap:
            reading_success, custom_image_bgr = cap.read()
            frame_number += 1

