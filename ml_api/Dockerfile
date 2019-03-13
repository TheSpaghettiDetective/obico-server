FROM nvidia/cuda:9.0-devel-ubuntu16.04

RUN apt update
RUN apt install -y vim ffmpeg libsm6 libxrender1 libfontconfig1 python3-pip
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 10
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 10

ADD . /app
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 3333
CMD ["sh", "-c", "newrelic-admin run-program python server.py"]
