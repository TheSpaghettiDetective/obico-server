#!python3

# pylint: disable=R, W0401, W0614, W0703
from enum import Enum
from lib.meta import Meta
from os import path

alt_names = None

darknet_ready = True
try:
    from lib.backend_darknet import YoloNet
except:
    darknet_ready = False

onnx_ready = True
try:
    from lib.backend_onnx import OnnxNet
except:
    onnx_ready = False


def load_net(config_path, meta_path, weight_path=None):

    def try_loading_net(config_path_inner, meta_path_inner, weight_paths_to_try):
        for use_gpu in [True, False]:
            for weight in weight_paths_to_try:
                net_main = None
                try:
                    print(f'Trying to load weight: {weight} - use_gpu = {use_gpu} ...')
                    if weight.endswith(".onnx"):
                        if not onnx_ready:
                            raise Exception('OnnxNet failed to be imported')
                        net_main = OnnxNet(weight, meta_path_inner, use_gpu)

                    elif weight.endswith(".darknet"):
                        if not darknet_ready:
                            raise Exception('YoloNet failed to be imported')
                        net_main = YoloNet(config_path, weight, meta_path)

                    else:
                        raise Exception(f'Can not recognize net from weight file surfix: {weight}')

                    print('Succeeded!')
                    return net_main
                except Exception as e:
                    print(f'Failed! - {e}')

        raise Exception(f'Failed to load any of these weights: {weight_paths_to_try}')

    global alt_names  # pylint: disable=W0603

    model_dir = path.join(path.dirname(path.realpath(__file__)), '..', 'model')
    default_weight_paths = [ path.join(model_dir, model_file) for model_file in ['model-weights.darknet', 'model-weights.onnx'] ] # TODO: Darknet has higher piroity now before ONNX accuracy is verified
    weight_paths_to_try = [weight_path,] if weight_path is not None else default_weight_paths
    net_main = try_loading_net(config_path, meta_path, weight_paths_to_try)

    if alt_names is None:
        # In Python 3, the metafile default access craps out on Windows (but not Linux)
        # Read the names file and create a list to feed to detect
        try:
            meta = Meta(meta_path)
            alt_names = meta.names
        except Exception:
            pass

    return net_main

def detect(net, image, thresh=.5, hier_thresh=.5, nms=.45, debug=False):
    return net.detect(net.meta, image, alt_names, thresh, hier_thresh, nms, debug)

