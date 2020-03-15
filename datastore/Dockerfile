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

RUN pip install flask

RUN apt-get update && apt-get install -y dos2unix

COPY start.sh start.sh
COPY datastore.py datastore.py

RUN chmod +x start.sh

RUN dos2unix /start.sh
RUN dos2unix /datastore.py

CMD ["/start.sh"]