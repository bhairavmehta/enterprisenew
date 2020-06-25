# IMAGE_ARCH Possible choices:
#  - arm64v8 (for x86 Windows or Linux)
ARG IMAGE_ARCH="arm64v8"
ARG IMAGE=${IMAGE_ARCH}/thebox_jetsonnano_rt

FROM ${IMAGE_ARCH}/thebox_jetsonnano_onnxrt AS onnxrt
FROM ${IMAGE_ARCH}/thebox_jetsonnano_rt

# ----- BEGIN: adopted from thebox_base Dockerfile -----

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
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

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

# ----- END: adopted from thebox_base Dockerfile -----


# ----- Install Build tools and Python
RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  virtualenv \
  python3-dev \
  gfortran \
  software-properties-common \
  unzip \
  wget \
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# ----- Install Library dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
  libhdf5-dev \
  libatlas-base-dev \
  liblapack-dev \
  libopenblas-dev \
  protobuf-compiler \
  libfreetype6-dev \
  libjemalloc1 \
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*
# workaround for hdf5 python package compilation issue
ENV HDF5_DIR=/usr/lib/aarch64-linux-gnu/hdf5/serial/

# install python dependencies
RUN pip3 install --upgrade \
  wheel \
  pip

# Copy over and install pre-built ONNXRuntime
COPY --from=onnxrt /dist/onnxruntime*.whl /tmp
RUN pip install /tmp/onnxruntime*.whl && \
  rm /tmp/*.whl

# Install Tensorflow
RUN pip install --pre --extra-index-url https://developer.download.nvidia.com/compute/redist/jp/v42 tensorflow-gpu

# ------ Run-time commands
CMD ["/bin/bash"]
