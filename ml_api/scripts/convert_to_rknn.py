#!/usr/bin/env python3
import sys
import argparse
import logging
from pathlib import Path

from rknn.api import RKNN as rknn

def ret_wrap(c, *args, **kwargs):
    ret_code = c(*args, **kwargs)
    if ret_code:
        raise RuntimeError(f"wrapped function retuned {ret_code}")

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser()
    parser.add_argument('model_path', type=Path)
    parser.add_argument('dataset', type=Path)
    parser.add_argument('platform')
    parser.add_argument('data_type')
    parser.add_argument('output_path', type=Path)
    parser.add_argument('-v', action='store_true', dest='verbose')
    args = parser.parse_args()


    rk = rknn(verbose=args.verbose)


    logger.info('Configuring RKNN')
    rk.config(
        mean_values=[ [0,0,0] ],
        std_values=[ [255,255,255] ],
        target_platform=args.platform
    )

    logger.info('Loading model')
    ret_wrap(rk.load_onnx, model=str(args.model_path.absolute()),
             inputs=['input'],
             input_size_list=[[1,3,416,416]]
             )

    should_quantize = args.data_type in ['i8','u8']

    logger.info('Building model')
    ret_wrap(rk.build, do_quantization=should_quantize, dataset=str(args.dataset.absolute()))

    logger.info('Exporting model')
    ret_wrap(rk.export_rknn, str(args.output_path.absolute()))

if __name__ == "__main__":
    main()