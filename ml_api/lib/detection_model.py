import os, sys
import cv2
from openvino.inference_engine import IENetwork, IECore
from argparse import ArgumentParser, SUPPRESS
import logging
from math import exp as exp
from time import time


OPENVINO_SCALARS = [2.75, 1.5]

class YoloParams:
    # ------------------------------------------- Extracting layer parameters ------------------------------------------
    # Magic numbers are copied from yolo samples
    def __init__(self, param, side, logger):
        self.num = 3 if 'num' not in param else int(param['num'])
        self.coords = 4 if 'coords' not in param else int(param['coords'])
        self.classes = 80 if 'classes' not in param else int(param['classes'])
        self.anchors = [10.0, 13.0, 16.0, 30.0, 33.0, 23.0, 30.0, 61.0, 62.0, 45.0, 59.0, 119.0, 116.0, 90.0, 156.0,
                        198.0,
                        373.0, 326.0] if 'anchors' not in param else [float(a) for a in param['anchors'].split(',')]

        if 'mask' in param:
            mask = [int(idx) for idx in param['mask'].split(',')]
            self.num = len(mask)

            maskedAnchors = []
            for idx in mask:
                maskedAnchors += [self.anchors[idx * 2], self.anchors[idx * 2 + 1]]
            self.anchors = maskedAnchors

        self.side = side
        self.isYoloV3 = 'mask' in param  # Weak way to determine but the only one.
        self.logger = logger


    def log_params(self):
        params_to_print = {'classes': self.classes, 'num': self.num, 'coords': self.coords, 'anchors': self.anchors}
        [self.logger.info("         {:8}: {}".format(param_name, param)) for param_name, param in params_to_print.items()]


def entry_index(side, coord, classes, location, entry):
    side_power_2 = side ** 2
    n = location // side_power_2
    loc = location % side_power_2
    return int(side_power_2 * (n * (coord + classes + 1) + entry) + loc)


def scale_bbox(x, y, h, w, class_id, confidence, h_scale, w_scale):
    xmin = int((x - w / 2) * w_scale)
    ymin = int((y - h / 2) * h_scale)
    xmax = int(xmin + w * w_scale)
    ymax = int(ymin + h * h_scale)
    return dict(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, class_id=class_id, confidence=confidence)


def parse_yolo_region(blob, resized_image_shape, original_im_shape, params, threshold):
    # ------------------------------------------ Validating output parameters ------------------------------------------
    _, _, out_blob_h, out_blob_w = blob.shape
    assert out_blob_w == out_blob_h, "Invalid size of output blob. It sould be in NCHW layout and height should " \
                                     "be equal to width. Current height = {}, current width = {}" \
                                     "".format(out_blob_h, out_blob_w)

    # ------------------------------------------ Extracting layer parameters -------------------------------------------
    orig_im_h, orig_im_w = original_im_shape
    resized_image_h, resized_image_w = resized_image_shape
    objects = list()
    predictions = blob.flatten()
    side_square = params.side * params.side

    # ------------------------------------------- Parsing YOLO Region output -------------------------------------------
    for i in range(side_square):
        row = i // params.side
        col = i % params.side
        for n in range(params.num):
            obj_index = entry_index(params.side, params.coords, params.classes, n * side_square + i, params.coords)
            scale = predictions[obj_index]
            if scale < threshold:
                continue
            box_index = entry_index(params.side, params.coords, params.classes, n * side_square + i, 0)
            # Network produces location predictions in absolute coordinates of feature maps.
            # Scale it to relative coordinates.
            x = (col + predictions[box_index + 0 * side_square]) / params.side
            y = (row + predictions[box_index + 1 * side_square]) / params.side
            # Value for exp is very big number in some cases so following construction is using here
            try:
                w_exp = exp(predictions[box_index + 2 * side_square])
                h_exp = exp(predictions[box_index + 3 * side_square])
            except OverflowError:
                continue
            # Depends on topology we need to normalize sizes by feature maps (up to YOLOv3) or by input shape (YOLOv3)
            w = w_exp * params.anchors[2 * n] / (resized_image_w if params.isYoloV3 else params.side)
            h = h_exp * params.anchors[2 * n + 1] / (resized_image_h if params.isYoloV3 else params.side)
            for j in range(params.classes):
                class_index = entry_index(params.side, params.coords, params.classes, n * side_square + i,
                                          params.coords + 1 + j)
                confidence = scale * predictions[class_index]
                if confidence < threshold:
                    continue

                # scale OpenVINO model more to get closer to YOLO2 model
                if confidence < .3:
                    confidence = confidence * OPENVINO_SCALARS[0]
                elif confidence < .6:
                    confidence = confidence * OPENVINO_SCALARS[1]

                objects.append(scale_bbox(x=x, y=y, h=h, w=w, class_id=j, confidence=confidence,
                                          h_scale=orig_im_h, w_scale=orig_im_w))
    return objects


def intersection_over_union(box_1, box_2):
    width_of_overlap_area = min(box_1['xmax'], box_2['xmax']) - max(box_1['xmin'], box_2['xmin'])
    height_of_overlap_area = min(box_1['ymax'], box_2['ymax']) - max(box_1['ymin'], box_2['ymin'])
    if width_of_overlap_area < 0 or height_of_overlap_area < 0:
        area_of_overlap = 0
    else:
        area_of_overlap = width_of_overlap_area * height_of_overlap_area
    box_1_area = (box_1['ymax'] - box_1['ymin']) * (box_1['xmax'] - box_1['xmin'])
    box_2_area = (box_2['ymax'] - box_2['ymin']) * (box_2['xmax'] - box_2['xmin'])
    area_of_union = box_1_area + box_2_area - area_of_overlap
    if area_of_union == 0:
        return 0
    return area_of_overlap / area_of_union


class OpenVinoModel:
    def __init__(self, net, exec_net, labels_map, n, c, w, h, input_blob):
        self.net = net
        self.exec_net = exec_net
        self.labels_map = labels_map
        self.n = n
        self.c = c
        self.w = w
        self.h = h
        self.input_blob = input_blob
        self.shape = (n, c, h, w)

    def params(self):
        return (self.net, self.exec_net, self.labels_map, self.n, self.c, self.w, self.h, self.input_blob)


openvino_model = None


def load_net(model_xml, labels_path, device, cpu_extension, log=None):
    global openvino_model

    if not os.path.exists(model_xml):
        raise ValueError("Invalid model xml path `"+os.path.abspath(model_xml)+"`")
    if not os.path.exists(labels_path):
        raise ValueError("Invalid model label path `"+os.path.abspath(labels_path)+"`")
    if device == "CPU" and (cpu_extension is None or not os.path.exists(cpu_extension)):
        raise ValueError("Invalid cpu extension path `"+os.path.abspath(cpu_extension)+"`")

    if log is None:
        log = logging.getLogger()

    if openvino_model is None:
        # plugin initialization for specified device and load extensions library if specified
        model_bin = os.path.splitext(model_xml)[0] + ".bin"
        if not os.path.exists(model_xml):
            raise ValueError("Invalid model bin path `"+os.path.abspath(model_bin)+"`")

        log.info("Creating Inference Engine...")
        ie = IECore()
        if device == "CPU" and cpu_extension is not None:
            ie.add_extension(cpu_extension, "CPU")

        # load the IR generated by the Model Optimizer (.xml and .bin files)
        print("Loading network files:\n\t{}\n\t{}".format(model_xml, model_bin))
        net = IENetwork(model=model_xml, weights=model_bin)

        # load the CPU extension for support specific layer
        if device == "CPU":
            supported_layers = ie.query_network(net, "CPU")
            not_supported_layers = [l for l in net.layers.keys() if l not in supported_layers]
            if len(not_supported_layers) != 0:
                log.error("Following layers are not supported by the plugin for specified device {}:\n {}".
                        format(device, ', '.join(not_supported_layers)))
                log.error("Please try to specify cpu extensions library path in sample's command line parameters using -l "
                        "or --cpu_extension command line argument")
                sys.exit(1)

        assert len(net.inputs.keys()) == 1, "Sample supports only YOLO V3 based single input topologies"

        # prepare inputs
        log.info("Preparing inputs")
        input_blob = next(iter(net.inputs))

        # defaulf batch_size is 1
        net.batch_size = 1

        # read and pre-process input images
        n, c, h, w = net.inputs[input_blob].shape

        # create map from labels
        if labels_path:
            with open(labels_path, 'r') as f:
                labels_map = [x.strip() for x in f]
        else:
            labels_map = None

        # load model to the plugin
        num_requests = 2
        log.info("Loading model to the plugin: num requests = %d" % num_requests)
        exec_net = ie.load_network(network=net, num_requests=num_requests, device_name=device)

        # create model class into global variable
        openvino_model = OpenVinoModel(net, exec_net, labels_map, n, c, w, h, input_blob)

    return openvino_model


def detect(model, frame, thresh=.5, iou_threshold=0.60, raw_output_message=False, logger=None, show=False):
    if logger is None:
        logger = logging.getLogger()

    render_time = 0
    parsing_time = 0
    cur_request_id = 0

    net, exec_net, labels_map, n, c, w, h, input_blob = model.params()

    # begin inference
    logger.info("Starting inference...")
    in_frame = cv2.resize(frame, (w, h))

    # resize input_frame to network size
    in_frame = in_frame.transpose((2, 0, 1))  # Change data layout from HWC to CHW
    in_frame = in_frame.reshape((n, c, h, w))

    # start inference
    start_time = time()
    #start = datetime.now()
    exec_net.start_async(request_id=cur_request_id, inputs={input_blob: in_frame})

    # collect object detection results
    objects = list()
    if exec_net.requests[cur_request_id].wait(-1) == 0:
        output = exec_net.requests[cur_request_id].outputs
        det_time = time() - start_time

        start_time = time()
        for layer_name, out_blob in output.items():
            out_blob = out_blob.reshape(net.layers[net.layers[layer_name].parents[0]].shape)
            layer_params = YoloParams(net.layers[layer_name].params, out_blob.shape[2], logger)
            #logger.info("Layer {} parameters: ".format(layer_name))
            #layer_params.log_params()
            objects += parse_yolo_region(out_blob, in_frame.shape[2:],
                                        frame.shape[:-1], layer_params,
                                        thresh)
        parsing_time = time() - start_time

    # filter overlapping boxes with respect to the --iou_threshold CLI parameter
    objects = sorted(objects, key=lambda obj : obj['confidence'], reverse=True)
    for i in range(len(objects)):
        if objects[i]['confidence'] == 0:
            continue
        for j in range(i + 1, len(objects)):
            if intersection_over_union(objects[i], objects[j]) > iou_threshold:
                objects[j]['confidence'] = 0

    # Drawing objects with respect to the --prob_threshold CLI parameter
    objects = [obj for obj in objects if obj['confidence'] >= thresh]

    if len(objects) and raw_output_message:
        logger.info("\nDetected boxes for batch {}:".format(1))
        logger.info(" Class ID | Confidence | XMIN | YMIN | XMAX | YMAX | COLOR ")

    detections = []

    origin_im_size = frame.shape[:-1]

    for obj in objects:
        # Validation bbox of detected object
        if obj['xmax'] > origin_im_size[1] or obj['ymax'] > origin_im_size[0] or obj['xmin'] < 0 or obj['ymin'] < 0:
            continue

        # convert bounding to yolo values
        w = obj['xmax'] - obj['xmin']
        h = obj['ymax'] - obj['ymin']
        w2 = w//2
        h2 = h//2

        # get matching label - always 'falure'
        det_label = labels_map[obj['class_id']] if labels_map and len(labels_map) >= obj['class_id'] else str(obj['class_id'])

        # create next detection value and add to list
        d = (det_label, float(obj['confidence']), (obj['xmin'] + w2, obj['ymin'] + h2, w, h))
        detections.append(d)

        color = (int(min(obj['class_id'] * 12.5, 255)), min(obj['class_id'] * 7, 255), min(obj['class_id'] * 5, 255))

        if raw_output_message:
            logger.info(
                "{:^9} | {:10f} | {:4} | {:4} | {:4} | {:4} | {} ".format(det_label, obj['confidence'], obj['xmin'],
                                                                            obj['ymin'], obj['xmax'], obj['ymax'],
                                                                            color))

        # draw bounding box, and label
        if show:
            (xc, yc, w, h) = map(int, d[2])
            cv2.rectangle(frame,(xc-w//2,yc-h//2),(xc+w//2,yc+h//2), (0,255,0), 2)
            #cv2.rectangle(frame, (obj['xmin'], obj['ymin']), (obj['xmax'], obj['ymax']), color, 2)
            cv2.putText(frame, det_label + ' ' + str(round(obj['confidence'] * 100, 1)) + ' %', (obj['xmin'], obj['ymin'] - 7), cv2.FONT_HERSHEY_COMPLEX, 0.6, (0,255,0), 1)

    if show:
        # Draw performance stats over frame
        inf_time_message = "Inference time: {:.3f} ms".format(det_time * 1e3)
        parsing_message = "YOLO parsing time is {:.3f} ms".format(parsing_time * 1e3)
        cv2.putText(frame, inf_time_message, (15, 15), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0), 1)
        cv2.putText(frame, parsing_message, (15, 30), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0), 1)
        #render_time_message = "OpenCV rendering time: {:.3f} ms".format(render_time * 1e3)
        #async_mode_message = "Async mode is off. Processing request {}".format(cur_request_id)
        #cv2.putText(frame, render_time_message, (15, 45), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0), 1)
        #cv2.putText(frame, async_mode_message, (10, int(origin_im_size[0] - 20)), cv2.FONT_HERSHEY_COMPLEX, 0.5, (10, 10, 200), 1)
        return frame

    if len(detections) > 1:
        detections = sorted(detections, key=lambda x: -x[1])

    return detections

def build_argparser():
    parser = ArgumentParser(add_help=False)
    args = parser.add_argument_group('Options')
    args.add_argument('-h', '--help', action='help', default=SUPPRESS, help='Show this help message and exit.')

    # model args
    args.add_argument("-m", "--model", help="Required. Path to an .xml file with a trained model.",
                      required=True, type=str, default=os.environ.get("MODEL_XML", None))
    args.add_argument("--labels", help="Optional. Labels mapping file", default=os.environ.get("MODEL_LABELS", None), type=str)
    args.add_argument("-d", "--device",
                      help="Optional. Specify the target device to infer on; CPU, GPU, FPGA, HDDL or MYRIAD is"
                           " acceptable. The sample will look for a suitable plugin for device specified. "
                           "Default value is CPU", default=os.environ.get("OPENVINO_DEVICE", "CPU"), type=str)
    args.add_argument("-l", "--cpu_extension",
                      help="Optional. Required for CPU custom layers. Absolute path to a shared library with "
                           "the kernels implementations.", type=str, default=os.environ.get("OPENVINO_CPU_EXTENSION", None))

    # input
    args.add_argument("-i", "--input", help="Required. Path to a image file.", required=True, type=str)
    # output
    args.add_argument("-o", "--output", help="Optional. Path to a image file.", required=False, default=None, type=str)

    # detection args
    args.add_argument("-t", "--prob_threshold", help="Optional. Probability threshold for detections filtering",
                      default=0.2, type=float)
    args.add_argument("-iout", "--iou_threshold", help="Optional. Intersection over union threshold for overlapping "
                                                       "detections filtering", default=0.45, type=float)
    args.add_argument("-ni", "--number_iter", help="Optional. Number of inference iterations", default=1, type=int)
    args.add_argument("-pc", "--perf_counts", help="Optional. Report performance counters", default=False,
                      action="store_true")
    args.add_argument("-r", "--raw_output_message", help="Optional. Output inference results raw values showing",
                      default=False, action="store_true")

    return parser


if __name__ == "__main__":
    logging.basicConfig(format="[ %(levelname)s ] %(message)s", level=logging.INFO, stream=sys.stdout)
    logger = logging.getLogger()

    args = build_argparser().parse_args()

    model = load_net(args.model, args.labels, args.device, args.cpu_extension, logger)

    custom_image_bgr = cv2.imread(args.input)

    print(detect(model, custom_image_bgr, thresh=args.prob_threshold, iou_threshold=args.iou_threshold, raw_output_message=args.raw_output_message))

