FROM thespaghettidetective/ml_api:base
WORKDIR /app
EXPOSE 3333

ADD . /app
RUN cp lib\model_$(uname --m).so lib\model.so && \
	cp lib\model_gpu_$(uname --m).so lib\model_gpu.so
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN wget --quiet -O model/model.weights $(cat model/model.weights.url | tr -d '\r')
