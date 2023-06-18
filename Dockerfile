FROM python:3.11.4-bullseye

RUN apt-get update && \
    apt-get -yq install ffmpeg

RUN mkdir -p /app

COPY codenarrative /app/codenarrative
COPY fonts /app/fonts
COPY sounds /app/sounds

COPY requirements.txt /app
COPY codenarrative.sh /app

RUN pip install -r app/requirements.txt

