# Self-contained web image: the Python 3.12 + Django 5.2 stack installs its
# dependencies directly, instead of inheriting them from the hand-built
# thespaghettidetective/web:base image (which is Python 3.10 and caps Pillow
# at 12.x). The steps mirror backend/Dockerfile.base so the two stay
# equivalent.
FROM python:3.12-alpine3.22

WORKDIR /app
EXPOSE 3334

RUN apk -U add bash vim ffmpeg postgresql-libs git openjpeg tiff
RUN apk add --virtual .build-deps g++ musl-dev postgresql-dev zlib-dev jpeg-dev libffi-dev openjpeg-dev tiff-dev openblas-dev \
    patch curl-dev python3-dev build-base freetype-dev lcms2-dev tk-dev tcl-dev  # Needed by /moonraker/scripts/moonraker-requirements.txt

# Checkout moonraker and lock the version so that we can use the metadata parser
RUN git clone https://github.com/Arksine/moonraker.git /moonraker
RUN git -C /moonraker checkout f735c0419444848b59342a98ad3532eef123ea46
ENV PYTHONPATH="${PYTHONPATH}:/moonraker"

# Requirements before the source, so editing code does not reinstall the
# dependencies — the same ordering the ml_api images use, and it now costs
# twice as much to get wrong since this builds on two runners per release.
COPY requirements.txt /app/
RUN CRYPTOGRAPHY_DONT_BUILD_RUST=1 pip install --no-cache-dir --upgrade pip \
 && CRYPTOGRAPHY_DONT_BUILD_RUST=1 pip install --no-cache-dir -r requirements.txt

# Same as the old base: drop the compile-time packages once the wheels are in
# place. The runtime libraries they pulled in survive because the runtime set
# (ffmpeg, postgresql-libs, openjpeg, tiff, python itself) still needs them.
RUN apk --purge del .build-deps

ADD ./ /app
