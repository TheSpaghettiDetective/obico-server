FROM thespaghettidetective/web:base-1.18

WORKDIR /app
EXPOSE 3334

RUN pip install --no-cache-dir -U pip pipenv==2022.12.19

COPY backend /app
COPY frontend /frontend
RUN pip install --no-cache-dir -r requirements.txt

CMD ["bash", "/app/run.sh"]
