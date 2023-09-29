FROM thespaghettidetective/web:base-1.13

WORKDIR /app
EXPOSE 3334

COPY backend/requirements.txt /app
RUN pip install -U pip \
    && pip install -r /app/requirements.txt

COPY backend /app
COPY frontend /frontend