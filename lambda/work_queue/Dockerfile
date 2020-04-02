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

RUN pip install redis \
                psycopg2==2.8.4

RUN apt-get update && apt-get install -y dos2unix

COPY populate_work_queue.py /populate_work_queue.py
RUN dos2unix /populate_work_queue.py

ARG POSTGRES_HOSTNAME="172.17.0.2"
ARG POSTGRES_PASSWORD="ackbar"
ARG REDIS_HOSTNAME="172.17.0.4"
ARG REDIS_PASSWORD="ackbar"
ENV POSTGRES_HOSTNAME="${POSTGRES_HOSTNAME}"
ENV POSTGRES_PASSWORD="${POSTGRES_PASSWORD}"
ENV REDIS_HOSTNAME="${REDIS_HOSTNAME}"
ENV REDIS_PASSWORD="${REDIS_PASSWORD}"

CMD ["/usr/bin/python3", "/populate_work_queue.py"]
