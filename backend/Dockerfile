FROM thespaghettidetective/web:base-1.18

WORKDIR /app
EXPOSE 3334

RUN pip install --no-cache-dir -U pip pipenv==2022.12.19

COPY backend /app
COPY frontend /frontend
RUN pip install --no-cache-dir -r requirements.txt

# Keep recordings in mounted config directory
# Implementation from https://github.com/imagegenius/docker-obico
RUN mkdir -p /data/media && \
    mkdir /app/static_build && \
    ln -s data/media /app/static_build/media
CMD ["/bin/sh", "/app/run.sh"]
