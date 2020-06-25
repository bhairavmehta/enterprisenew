# using a smaller image doesn't save us any space as the layers are used by the other images.
ARG VERSION_ID
FROM ubuntu:${VERSION_ID}

RUN mkdir -p /tmp
COPY ./sdkmanager_*.deb /tmp

# Install SDK manager first
RUN apt-get update
RUN apt install -y libcanberra-gtk-module libgconf-2-4 libgtk-3-0 libxss1 libnss3 xvfb lsb-release
RUN dpkg -i /tmp/sdkmanager_*.deb || \
    apt-get -y -f install && \
    dpkg -i /tmp/sdkmanager_*.deb

# Copy over the script for downloading dependencies
COPY ./download-jetpack.sh  ./tmp

# RUN XVFB then SDK manager
ARG NV_USER=
ARG NV_LOGIN_TYPE=devzone

ENV NV_USER=${NV_USER}
ENV NV_LOGIN_TYPE=${NV_LOGIN_TYPE}

RUN mkdir -p /data

# Create a dummy user (as SDKManager picks on running this as root)
RUN groupadd -r sdkgrp && useradd -m -r -g sdkgrp sdkuser
RUN mkdir /h
RUN echo export DISPLAY=:1.0 > /home/sdkuser/.bashrc && \
    echo export DEVICE_ID=P3448-0000 >> /home/sdkuser/.bashrc && \
    echo export DEVICE_OPTION=--target >> /home/sdkuser/.bashrc && \
    echo export NV_USER=${NV_USER} >> /home/sdkuser/.bashrc && \
    echo export NV_LOGIN_TYPE=${NV_LOGIN_TYPE} >> /home/sdkuser/.bashrc && \
    echo export PRODUCT=Jetson >> /home/sdkuser/.bashrc && \
    echo export JETPACK_VERSION=GA_4.2.2 >> /home/sdkuser/.bashrc && \
    echo export TARGET_OS=Linux >> /home/sdkuser/.bashrc && \
    echo export ACCEPT_SDK_LICENCE=accept >> /home/sdkuser/.bashrc

# During run time, run SDKManager
CMD Xvfb :1 -screen 0 1024x768x16 &> xvfb.log && \
    su -l sdkuser -c "/bin/bash -c \"source /home/sdkuser/.bashrc; /tmp/download-jetpack.sh\""
