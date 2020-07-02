FROM ubuntu:16.04

RUN apt-get update && \
        apt-get install -y software-properties-common && \
        add-apt-repository ppa:deadsnakes/ppa && \
        apt-get update -y  && \
        apt-get install -y build-essential python3.6 python3.6-dev python3-pip && \
        apt-get install -y git  && \
        python3.6 -m pip install pip --upgrade && \
        python3.6 -m pip install wheel && \
        mkdir $HOME/thebox

COPY src/ /root/thebox/src
COPY requirements.txt /root/thebox

RUN python3.6 -m pip install -r /root/thebox/requirements.txt
RUN for file in /root/thebox/src/thebox_testapp/*/requirements.txt; do python3.6 -m  pip install -r $file; done
ENV PYTHONPATH=/root/thebox/src

WORKDIR /root/thebox/src/web_app