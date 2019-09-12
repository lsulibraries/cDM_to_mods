# docker build -t ubuntu-14.04-python3.6 .

FROM ubuntu:18.04

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
        wget \
        libssl-dev \
        openssl \
        cython3 \
        zlib1g-dev \
        python-dev \
        libxml2-dev \
        libxslt-dev \
        lib32z1-dev \
        default-jre

WORKDIR /tmp

RUN wget https://www.python.org/ftp/python/3.6.9/Python-3.6.9.tar.xz \
    && tar -xf Python-3.6.9.tar.xz \
    && cd /tmp/Python-3.6.9 \
    && ./configure \
    && make \
    && make install \
    && rm -rf /tmp/Python-3.6.9.tar.xz /tmp/Python-3.6.9

RUN pip3 install -U pip \
    && pip3 install -U lxml openpyxl
