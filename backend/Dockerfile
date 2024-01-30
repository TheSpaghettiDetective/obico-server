FROM thespaghettidetective/web:base-1.16

WORKDIR /app
EXPOSE 3334

RUN pip install --no-cache-dir --upgrade \
    pip==23.3.2 \
    pipenv==2022.12.19

COPY ./ /app
RUN pip install --no-cache-dir -r requirements.txt
