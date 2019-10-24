# Run TSD server on Jetson Nano

*Attribution: This guide is adopted from [Raymond's scripts](https://gist.github.com/RaymondHimle/5c06454f09f0e370ec0673835fb53dba).*

## Compile on Jetson device

```
wget https://github.com/AlexeyAB/darknet/archive/darknet_yolo_v3.zip
unzip darknet_yolo_v3.zip
cd darknet-darknet_yolo_v3/
```

Edit the `Makefile`. Set `OPENMP=1, LIBSO=1, OPENCV=1, and NVCC=/usr/local/cuda/bin/nvcc`.

```
make
mv libdarknet.so model.so
```

Edit the `Makefile`. Set `GPU=1` (have not tried with CUDNN=1)

```
make
mv libdarknet.so model_gpu.so
```

## Change `Dockerfile` as follows:

```
FROM jetsistant/cuda-jetpack:4.2.1-devel
WORKDIR /app
EXPOSE 3333

ADD ./libopencv_3.3.1-2-g31ccdfe11_arm64.deb .
ARG DEBIAN_FRONTEND=noninteractive
RUN rm -rf /etc/apt/sources.list.d/cuda.list && \
    apt update && \
  	dpkg --install /app/libopencv_3.3.1-2-g31ccdfe11_arm64.deb && /
	  apt install --no-install-recommends -y python3-opencv libsm6 libxrender1 libfontconfig1 python3-pip python3-setuptools vim ffmpeg wget curl && \
    rm -rf /var/lib/apt/lists/* && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3 10 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 10

RUN pip install --upgrade pip
ADD requirements.txt .
RUN pip install -r requirements.txt

#
ADD . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN wget --quiet -O model/model.weights $(cat model/model.weights.url | tr -d '\r')
```

## Other notes

### Steps I followed to get TSD on Jetson Nano

1. Install PIP and use pip to install docker-compose 1.24 (Missing these steps)

1. Move the compiled so files to the ml_api/bin folder replacing exsisting files

1. Use the NVIDIA SDK to download the libopencv_3.3.1-2-g31ccdfe11_arm64.deb file and place it in the ml_api folder.

1. Edit docker-compose.yml uncomment and set HAS_GPU to True

1. Create docker-compose.override.yml and add the following

```
version: '2.4'

services:
  ml_api:
    runtime: nvidia
```
