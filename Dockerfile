FROM ubuntu:latest
MAINTAINER "Marcel Gietzmann-Sanders" "marcelsanders96@gmail.com"

RUN apt-get -y update && \
	apt-get -y upgrade && \
	apt-get install -y build-essential

# basic editor installation
RUN apt-get -y install vim

# add python and libraries
RUN apt-get -y install python3.6 && \
	apt-get -y install python3-pip && \
	pip3 install --upgrade setuptools pip
RUN echo "alias python=python3.6" >> /root/.bashrc

RUN pip install tensorflow==2.1.0 \
				pandas==1.0.1 \
				scikit-learn==0.22.1 \
				seaborn==0.10.0 \
				jupyterlab==1.2.6 \
                Pillow==7.0.0 \
                tqdm==4.43.0 \
                azureml-sdk[notebooks,automl] \
                azure-storage-blob

# setting up ssh server
RUN apt-get update && apt-get install -y openssh-server
RUN mkdir /var/run/sshd
RUN echo "root:ackbar" | chpasswd
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config

# SSH login fix. Otherwise user is kicked off after login
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22 8888

# rmate for piping sublime
RUN wget -O /usr/local/bin/rmate https://raw.github.com/aurora/rmate/master/rmate
RUN chmod a+x /usr/local/bin/rmate

# install git
RUN apt-get -y install git

# clone ackbar
RUN git clone https://github.com/erebuseternal/ackbar.git

CMD ["/usr/sbin/sshd", "-D"]
