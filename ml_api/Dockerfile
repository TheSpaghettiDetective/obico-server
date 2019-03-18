FROM nvidia/cuda:9.0-devel-ubuntu16.04

RUN apt update
RUN apt install -y libsm6 libxrender1 libfontconfig1 python3-pip vim ffmpeg wget curl
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 10
RUN update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 10

ADD . /app
WORKDIR /app
RUN wget --quiet -O model/model.weights "https://storage.googleapis.com/prod-pub-static/ml-models/model.weights-03132019"
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 3333
CMD ["sh", "-c", "newrelic-admin run-program python server.py"]
