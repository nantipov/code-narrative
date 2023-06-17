FROM python:3.11.4-bullseye

RUN apt-get update && \
    apt-get -yq install ffmpeg

RUN mkdir -p /app

COPY codenarrative /app
COPY requirements.txt /app

RUN pip install -r app/requirements.txt

ENV PYTHONPATH=/app

RUN echo '#!/usr/bin/env sh' > /app/codenarrative.sh && \
    echo 'python3 /app/codenarrative/main.py $*' >> /app/codenarrative.sh

