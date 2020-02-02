FROM diveboatslave/openvino-2019.r3.376:latest

WORKDIR /app
EXPOSE 3333

RUN apt-get update && \
    apt-get install --no-install-recommends -y apt-utils python3-pip python3-setuptools nano wget curl ncdu && \
    rm -rf /var/lib/apt/lists/* && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3 10 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 10

ADD server.py /app
ADD auth.py /app
ADD wsgi.py /app
ADD lib/ /app/lib
ADD model/ /app/model

RUN pip install --upgrade pip
ADD requirements.txt requirements_x86_64.txt ./
RUN pip install -r requirements_x86_64.txt

ENV OPENVINO_DEVICE=CPU
ENV OPENVINO_CPU_EXTENSION=/opt/intel/openvino/deployment_tools/inference_engine/lib/intel64/libcpu_extension_avx2.so

# download OpenVINO IR model
RUN wget --quiet -O ./model/model.bin $(cat ./model/model.bin.url | tr -d '\r')

CMD ["/bin/bash"]
