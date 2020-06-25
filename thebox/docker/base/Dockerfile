# Note:
#   For preparation, on the host please run following once as admin/root:
#      docker run --rm --privileged multiarch/qemu-user-static:register

# IMAGE_ARCH Possible choices:
#  - arm64v8 (for Jetson)
#  - arm32v7 (for raspbian)
#  - amd64 (for x86 Windows or Linux)
ARG IMAGE_ARCH=amd64

# ----- Get QEMU binaries -----
FROM debian:buster
RUN apt-get update && apt-get install -qqy qemu-user-static

# ----- Base Image -----
FROM ${IMAGE_ARCH}/ubuntu:18.04

ARG IMAGE_ARCH=amd64

# ----- Setup QEMU -----

# Copy QEMU bits for cross platform execution
# NOTE: on Windows build we seem to have a problem expanding the ARG correctly
#       for COPY command, so for now we just copy all the qemu binaries
COPY --from=0 /usr/bin/qemu-aarch64-static /usr/bin/qemu-aarch64-static
COPY --from=0 /usr/bin/qemu-arm-static /usr/bin/qemu-arm-static

# ----- Install required libraries -----

# prevent any interactive configrations
ENV DEBIAN_FRONTEND=noninteractive

# install python and other prerequisites
RUN apt-get update && apt-get install -y --no-install-recommends \
  python3 \
  python3-pip \
  python3-setuptools \
  libgomp1 \
  wait-for-it \
  locales \
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# Set the locale (required for Remote Container debugging)
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
  locale-gen
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8  

RUN pip3 install --upgrade \
  wheel \
  pip

# on ARM or ARM64, need to install compiler tool chains and python header
# as those packages need to be built from source
RUN if [ "$IMAGE_ARCH" != "amd64" ]; then \
  apt-get update && apt-get install -y --no-install-recommends \
  make \
  cmake \
  gcc \
  g++ \
  python3-dev \
  libssl-dev \
  zlib1g-dev \
  git \
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* ; \
  fi

# on ARM or ARM64, librdkafka need to be built separately
RUN if [ "$IMAGE_ARCH" != "amd64" ]; then \
  mkdir /root/github && cd /root/github && \
  git clone https://github.com/edenhill/librdkafka && \
  cd librdkafka && \
  ./configure --prefix=/usr && \
  make && \
  make install && \
  cd /root \
  && \
  rm -rf /root/github/* ; \
  fi

# install common python dependencies
ARG CHECKSUM_PACKAGELIST
RUN mkdir -p /tmp
COPY PythonPackageList.txt /tmp
RUN pip install -r /tmp/PythonPackageList.txt -v

# install wait-for-deps script tool
COPY wait-for-deps.sh.temp /usr/bin/wait-for-deps.sh

RUN chmod 755 /usr/bin/wait-for-deps.sh
