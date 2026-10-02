FROM thespaghettidetective/web:base-1.18

WORKDIR /app
EXPOSE 3334

RUN pip install -U pip pipenv==2022.12.19

# Requirements before the source, so editing code does not reinstall the
# dependencies — the same ordering the ml_api images use, and it now costs
# twice as much to get wrong since this builds on two runners per release.
COPY requirements.txt /app/
RUN pip install -r requirements.txt

ADD ./ /app
