#==============================================================================
# CPU small image used as a base for the CPU-based builds
# 31 MiB compressed download
#==============================================================================
FROM debian:bullseye-slim as cpu_base
RUN apt update && apt install -y ca-certificates
# -----------------------------------------------------------------------------
# Download model weigths. They are later used many times, this will cache them
# -----------------------------------------------------------------------------
FROM cpu_base as models
RUN apt install -y wget
WORKDIR /app
ADD model/*.url /app/
RUN wget --quiet -O model-weights.darknet $(cat model-weights.darknet.url | tr -d '\r')
RUN wget --quiet -O model-weights.onnx $(cat model-weights.onnx.url | tr -d '\r')
# -----------------------------------------------------------------------------
# Cuda image with cuDNN dev version libraries, required to compile darknet
# Building Darknet-cuda-cudnn image
# -----------------------------------------------------------------------------
FROM nvcr.io/nvidia/cuda:11.4.3-cudnn8-devel-ubuntu20.04 as gpu_build_darknet
WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y ca-certificates build-essential gcc g++ cmake git
WORKDIR /app
RUN git clone https://github.com/AlexeyAB/darknet --depth 1
# compile GPU version
RUN cd darknet \
  && sed -i 's/GPU=0/GPU=1/' Makefile \
  && sed -i 's/CUDNN=0/CUDNN=1/' Makefile \
  && sed -i 's/CUDNN_HALF=0/CUDNN_HALF=1/' Makefile \
  && sed -i 's/LIBSO=0/LIBSO=1/' Makefile \
  && make -j 4 && mv libdarknet.so libdarknet_gpu.so
# compile CPU version
RUN cd darknet \
  && sed -i 's/GPU=1/GPU=0/' Makefile \
  && sed -i 's/CUDNN=1/CUDNN=0/' Makefile \
  && sed -i 's/CUDNN_HALF=1/CUDNN_HALF=0/' Makefile \
  && make -j 4 
# -----------------------------------------------------------------------------
# Cuda image with cuDNN runtime (smaller) without dev packages
# Output: GPU + CPU image
# -----------------------------------------------------------------------------
FROM nvcr.io/nvidia/cuda:11.4.3-cudnn8-runtime-ubuntu20.04 as ml_api
WORKDIR /app
RUN apt update && apt install -y ca-certificates python3-pip wget
RUN pip install --upgrade pip
ADD requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install opencv_python_headless onnxruntime-gpu
EXPOSE 3333
COPY --from=gpu_build_darknet /app/darknet/libdarknet.so bin/libdarknet.so
COPY --from=gpu_build_darknet /app/darknet/libdarknet_gpu.so bin/libdarknet_gpu.so
COPY --from=models /app/model-weights.darknet /app/model/
COPY --from=models /app/model-weights.onnx /app/model/
ADD . /app

#------------------------------------------------------------------------------
# Builder: CPU-build-darknet
#------------------------------------------------------------------------------
FROM cpu_base as cpu_build_darknet
RUN apt install -y build-essential gcc g++ cmake git
WORKDIR /app
RUN git clone https://github.com/AlexeyAB/darknet --depth 1
RUN cd darknet \
  && sed -i 's/LIBSO=0/LIBSO=1/' Makefile \
  && make -j 4
#------------------------------------------------------------------------------
# Output: CPU-only image (much smaller and will work on SBC like Rasperry Pi)
#------------------------------------------------------------------------------
FROM cpu_base as ml_api_cpu
EXPOSE 3333
RUN apt install -y python3-pip
RUN pip install --upgrade pip
ADD requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install opencv_python_headless onnxruntime
WORKDIR /app
COPY --from=cpu_build_darknet /app/darknet/libdarknet.so bin/libdarknet.so
COPY --from=models /app/model-weights.darknet /app/model/
COPY --from=models /app/model-weights.onnx /app/model/
ADD . /app

#==============================================================================
# Builder: Jetson-specific, Darknet-gpu version
#==============================================================================
# this will not use cuDNN because no headers included
# should be compatible with Jetpack 4xx
FROM nvcr.io/nvidia/l4t-tensorrt:r8.0.1-runtime as jetson_compile_darknet 
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y ca-certificates build-essential gcc g++ cmake git
WORKDIR /app
RUN git clone https://github.com/AlexeyAB/darknet --depth 1
ENV LIBRARY_PATH="${LIBRARY_PATH}:/usr/local/cuda/targets/aarch64-linux/lib:/usr/local/cuda/targets/aarch64-linux/lib/stubs"
# compile CPU version
RUN cd darknet \
  && sed -i 's/LIBSO=0/LIBSO=1/' Makefile \
  && make -j 4 && mv libdarknet.so libdarknet_cpu.so
# compile GPU version
RUN cd darknet \
  && sed -i 's/GPU=0/GPU=1/' Makefile \
  && sed -i 's/lcudart/lcudart_static -ldl -lrt/' Makefile \
  && make -j 4 && mv libdarknet.so libdarknet_gpu.so

  # these options do not work in 8.0.1 unfortunately
  # && sed -i 's/CUDNN=0/CUDNN=1/' Makefile \
  # && sed -i 's/CUDNN_HALF=0/CUDNN_HALF=1/' Makefile \
  # && sed -i 's/CUDNN=1/CUDNN=0/' Makefile \
  # && sed -i 's/CUDNN_HALF=1/CUDNN_HALF=0/' Makefile \

# Output image will not have darknet compilation layers to make it smaller
FROM nvcr.io/nvidia/l4t-tensorrt:r8.0.1-runtime as ml_api_jetson
WORKDIR /app
EXPOSE 3333
RUN pip install --upgrade pip
ADD requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install opencv_python_headless
COPY --from=jetson_compile_darknet /app/darknet/libdarknet_cpu.so bin/libdarknet.so
COPY --from=jetson_compile_darknet /app/darknet/libdarknet_gpu.so bin/libdarknet_gpu.so
COPY --from=models /app/model-weights.darknet /app/model/
COPY --from=models /app/model-weights.onnx /app/model/
# Some hacks to make darknet see cuda libraries. May fail easily
# this is only needed for Jetpack 4x and will not be needed for Jetpack 5
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/cuda/targets/aarch64-linux/lib"
# https://elinux.org/Jetson_Zoo#ONNX_Runtime
# May be unsafe to use such files, Todo: recompile onnx runtime
RUN wget https://nvidia.box.com/shared/static/2sv2fv1wseihaw8ym0d4srz41dzljwxh.whl -O onnxruntime_gpu-1.11.0-cp38-none-any.whl
RUN pip3 install onnxruntime_gpu-1.11.0-cp38-none-any.whl
ADD . /app

