#Running ML_api container

ML algorithms can be executed with different hardware and software options:

* x86_64 with CPU hardware without GPU, with `Darknet` or `ONNX` runtime.
* x86_64 with GPU (CUDA), with `Darknet` or `ONNX` runtime.
* ARM64 with CPU hardware, i.e. Raspberry PI 4, with `ONNX` runtime.
* ARM with GPU (CDUA), i.e. `Nvidia Jetson` devices with `Darknet` or `ONNX` runtime.

Darknet is written by Yolo2 author and you can find more details [here](https://github.com/AlexeyAB/darknet).
ONNX is Microsft-powered set of libraries and standards to execute neural networks on a different hardware.
More details about ONNX can be found [here](https://onnxruntime.ai/).

All suitable containers are build and now stored at docker.io registry, so you 
probably don't need to compile them (takes hours). But if that is needed, you can 
use [this script](building_docker_images.md).

By default, containers are run with `Darknet` + `CPU` method. This is what we had in previous
versions of TSD. Changing the library and hardware usage can be done with environment variables.
Assuming, the default (Darknet + CPU) is run with `cd obico-server && docker-compose up -d`, to run
a different version you can use:

* Darknet + *GPU*: `cd obico-server && ML_PROCESSOR=gpu docker-compose up -d`
* ONNX + *CPU*: `cd obico-server && ML_RUNTIME=onnx docker-compose -f docker-compose.yml -f docker-compose.nvidia.yml up -d`
* ONNX + *GPU*: `cd obico-server && ML_RUNTIME=onnx ML_PROCESSOR=gpu docker-compose -f docker-compose.yml -f docker-compose.nvidia.yml up -d`

