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
# Cuda image with cuDNN dev version libraries
# -----------------------------------------------------------------------------
FROM nvcr.io/nvidia/cuda:11.4.3-cudnn8-devel-ubuntu20.04 as cuda-dev 
WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y ca-certificates build-essential gcc g++ cmake git
# -----------------------------------------------------------------------------
# Cuda image with cuDNN runtime (smaller) 
# -----------------------------------------------------------------------------
FROM nvcr.io/nvidia/cuda:11.4.3-cudnn8-runtime-ubuntu20.04 as cuda-runtime
WORKDIR /app
RUN apt update && apt install -y ca-certificates python3-pip wget

RUN pip install --upgrade pip
ADD requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install opencv_python_headless
# -----------------------------------------------------------------------------
# Building Darknet-cuda-cudnn image
# -----------------------------------------------------------------------------
FROM cuda-dev as gpu_build_darknet
WORKDIR /app
RUN git clone https://github.com/AlexeyAB/darknet --depth 1
RUN cd darknet \
  && sed -i 's/GPU=0/GPU=1/' Makefile \
  && sed -i 's/CUDNN=0/CUDNN=1/' Makefile \
  && sed -i 's/CUDNN_HALF=0/CUDNN_HALF=1/' Makefile \
  && sed -i 's/LIBSO=0/LIBSO=1/' Makefile \
  && make
# -----------------------------------------------------------------------------
# Output: Darknet ML-api image
# -----------------------------------------------------------------------------
FROM cuda-runtime as ml_api_darknet_gpu
EXPOSE 3333
WORKDIR /app

ADD . /app
COPY --from=gpu_build_darknet /app/darknet/libdarknet.so bin/libdarknet.so
COPY --from=models /app/model-weights.darknet /app/model/

# -----------------------------------------------------------------------------
# Output: Onnx ML-api image
# -----------------------------------------------------------------------------
FROM cuda-runtime as ml_api_onnx_gpu
EXPOSE 3333
RUN pip install onnxruntime-gpu
WORKDIR /app

ADD . /app
COPY --from=models /app/model-weights.onnx /app/model/
#------------------------------------------------------------------------------
# Builder: CPU-build-darknet
#------------------------------------------------------------------------------
FROM cpu_base as cpu_build_darknet
RUN apt install -y build-essential gcc g++ cmake git
WORKDIR /app
RUN git clone https://github.com/AlexeyAB/darknet --depth 1
RUN cd darknet \
  && sed -i 's/LIBSO=0/LIBSO=1/' Makefile \
  && make
#------------------------------------------------------------------------------
# Output: CPU-darknet
#------------------------------------------------------------------------------
FROM cpu_base as ml_api_darknet_cpu
EXPOSE 3333
RUN apt install -y python3-pip
RUN pip install --upgrade pip
ADD requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install opencv_python_headless
ADD . /app
WORKDIR /app
COPY --from=cpu_build_darknet /app/darknet/libdarknet.so bin/libdarknet.so
COPY --from=models /app/model-weights.darknet /app/model/

#------------------------------------------------------------------------------
# Output: CPU-onnx
#------------------------------------------------------------------------------
FROM cpu_base as ml_api_onnx_cpu
EXPOSE 3333
RUN apt install -y python3-pip
RUN pip install --upgrade pip
ADD requirements.txt ./
RUN pip install -r requirements.txt
RUN echo 4
RUN uname -a
RUN pip install opencv_python_headless onnxruntime
ADD . /app
WORKDIR /app
COPY --from=models /app/model-weights.onnx /app/model/

#==============================================================================
# Builder: Jetson-specific, Darknet-gpu version
#==============================================================================
# this will not use cuDNN because no headers included
# should be compatible with Jetpack 4xx
FROM nvcr.io/nvidia/l4t-tensorrt:r8.0.1-runtime as l4t-devel
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y ca-certificates build-essential gcc g++ cmake git
WORKDIR /app
RUN git clone https://github.com/AlexeyAB/darknet --depth 1
ENV LIBRARY_PATH="${LIBRARY_PATH}:/usr/local/cuda/targets/aarch64-linux/lib:/usr/local/cuda/targets/aarch64-linux/lib/stubs"
RUN cd darknet \
  && sed -i 's/GPU=0/GPU=1/' Makefile \
  && sed -i 's/LIBSO=0/LIBSO=1/' Makefile \
  && sed -i 's/lcudart/lcudart_static -ldl -lrt/' Makefile \
  && make -j 4
# no cudnn headers in 8.0.1
#  && sed -i 's/CUDNN=0/CUDNN=1/' Makefile \

FROM nvcr.io/nvidia/l4t-tensorrt:r8.0.1-runtime as ml_api_darknet_gpu_l4t
WORKDIR /app
EXPOSE 3333
RUN pip install --upgrade pip
ADD requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install opencv_python_headless
ADD . /app
COPY --from=l4t-devel /app/darknet/libdarknet.so bin/libdarknet.so
COPY --from=models /app/model-weights.darknet /app/model/
ENV LD_LIBRARY_PATH="${LD_LIBRARY_PATH}:/usr/local/cuda/targets/aarch64-linux/lib"
RUN cp /usr/local/cuda/targets/aarch64-linux/lib/stubs/libcuda.so /usr/local/cuda/targets/aarch64-linux/lib/libcuda.so.1

#==============================================================================
# Output: Jetson-specific, Onnx-gpu version
#==============================================================================
# 8.0.1 version has Cuda 10, and onnxruntime 1.11 needs Cuda 10 
# and jetpack 4 has cuda 10
# for a modern cuda, need to recompile onnxruntime from source and have Jetpack 5 
# (AGX Xavier)
FROM nvcr.io/nvidia/l4t-tensorrt:r8.0.1-runtime as ml_api_onnx_gpu_l4t
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y wget
EXPOSE 3333
WORKDIR /app
RUN pip install --upgrade pip
ADD requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install opencv_python_headless
# https://elinux.org/Jetson_Zoo#ONNX_Runtime
RUN wget https://nvidia.box.com/shared/static/2sv2fv1wseihaw8ym0d4srz41dzljwxh.whl -O onnxruntime_gpu-1.11.0-cp38-none-any.whl
RUN pip3 install onnxruntime_gpu-1.11.0-cp38-none-any.whl
ADD . /app
COPY --from=models /app/model-weights.onnx /app/model/

