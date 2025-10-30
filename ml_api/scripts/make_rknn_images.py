#!/usr/bin/env python3
import argparse
import os
from os import PathLike
from pathlib import Path
from typing import Mapping, Callable

from rknn.api import RKNN

CONFIGURATIONS = {
    "rk3562": {},
    "rk3566": {},
    "rk3568": {},
    "rk3576": {},
    "rk3588": {},
    # "rv1103": {}, #  Requires quantization
    # "rv1106": {}, #  Requires quantization
    "rv1126b": {}
}

class RKNNSession(object):
    def __init__(self, *args, **kwargs):
        self.__rknn_args = args
        self.__rknn_kwargs = kwargs

    def __enter__(self):
        self.__rknn = RKNN(*self.__rknn_args, ** self.__rknn_kwargs)
        return self.__rknn

    def __exit__(self, typ, val, tb):
        self.__rknn.release()

def checked_call(c: Callable, *args, **kwargs):
    ret = c(*args, **kwargs)
    if ret:
        raise RuntimeError(f'Wrapped {c.__name__} returned {ret}')

def build_configuration(config_name:str, config_opts: Mapping, source_model: os.PathLike, load_opts:Mapping, build_opts: Mapping, dest_path: PathLike) -> None:
    if Path(dest_path).exists():
        print(f"Skipping {config_name} as output already exists")
        return
    print(f"Building {config_name}")
    with RKNNSession() as rk:
        rk.config(
            mean_values=[[0, 0, 0]],
            std_values=[[255, 255, 255]],
            target_platform=config_name
        )
        checked_call(rk.load_onnx, model=str(source_model), **load_opts)
        checked_call(rk.build, **build_opts)
        checked_call(rk.export_rknn, str(dest_path))

def build_configurations(source_model: PathLike, configs: Mapping, base_path: PathLike):
    base_path = Path(base_path)
    base_path.mkdir(exist_ok=True)

    for conf_name, conf_data in configs.items():
        build_opts = {}
        if quantize_dataset := conf_data.get('dataset'):
            build_opts['do_quantization'] = True
            build_opts['dataset'] = quantize_dataset
        else:
            build_opts['do_quantization'] = False

        conf_target = base_path / f'obico-ml-{conf_name}-fp.rknn'
        build_configuration(conf_name, conf_data, source_model, {}, build_opts, conf_target)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source_model', help="The source ONNX model to build from", type=Path)
    parser.add_argument('destination_path', help="Directory to place models in, created if it does not exist", type=Path)
    args = parser.parse_args()
    build_configurations(args.source_model, CONFIGURATIONS, args.destination_path)

if __name__ == "__main__":
    main()