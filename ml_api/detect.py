#!python3

from lib.detection_model import *

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
        net_main_1.force_cpu()

    import cv2
    from dataclasses import asdict
    import json
    from lib.geometry import compare_detections, Detection

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

    detections = Detection.from_tuple_list(detections)
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

