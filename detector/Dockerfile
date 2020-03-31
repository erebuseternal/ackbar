FROM ubuntu:latest
MAINTAINER "Marcel Gietzmann-Sanders" "marcelsanders96@gmail.com"

RUN apt-get -y update && \
	apt-get -y upgrade && \
	apt-get install -y build-essential && \
	apt-get install -y libpq-dev

# basic editor installation
RUN apt-get -y install vim

# add python and libraries
RUN apt-get -y install python3.6 && \
	apt-get -y install python3-pip && \
	pip3 install --upgrade setuptools pip
RUN echo "alias python=python3.6" >> /root/.bashrc

RUN pip install tensorflow==2.1.0 \
				pandas==1.0.1 \
                Pillow==7.0.0 \
                tqdm==4.43.0 \
                psycopg2==2.8.4 \
                requests

RUN apt-get update && apt-get install -y dos2unix
RUN apt-get install -y wget

# setup environment variables
ARG POSTGRES_HOSTNAME="172.17.0.2"
ARG POSTGRES_PASSWORD="ackbar"
ARG MODEL_PATH="/mega_detector_v3"
ARG BATCH_SIZE="1"
ARG STORAGE_HOSTNAME="172.17.0.3"
ENV POSTGRES_HOSTNAME="${POSTGRES_HOSTNAME}"
ENV POSTGRES_PASSWORD="${POSTGRES_PASSWORD}"
ENV MODEL_PATH="${MODEL_PATH}"
ENV BATCH_SIZE="${BATCH_SIZE}"
ENV STORAGE_HOSTNAME="${STORAGE_HOSTNAME}"

# get the saved model
COPY pull_megadetector.sh /pull_megadetector.sh
RUN dos2unix /pull_megadetector.sh
RUN /pull_megadetector.sh

# get the detector code
COPY detect.py /detect.py
RUN dos2unix /detect.py

CMD ["/usr/bin/python3", "/detect.py"]