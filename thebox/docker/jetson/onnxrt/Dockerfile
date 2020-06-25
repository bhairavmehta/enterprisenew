# ---- Base image for compiling onnxruntime
FROM arm64v8/thebox_jetsonnano_dev

# Installing dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    sudo \
    build-essential \
    curl \
    libcurl4-openssl-dev \
    libssl-dev \
    wget \
    python3 \
    python3-pip \
    python3-dev \
    git \
    tar \
    zlib1g \
    zlib1g-dev \
    libatlas-base-dev \
    && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
RUN pip3 install --upgrade setuptools
RUN pip3 install --upgrade wheel
RUN pip3 install numpy

# Build the latest cmake
WORKDIR /code
RUN wget https://github.com/Kitware/CMake/releases/download/v3.14.3/cmake-3.14.3.tar.gz
RUN tar zxf cmake-3.14.3.tar.gz

WORKDIR /code/cmake-3.14.3
RUN ./configure --system-curl
RUN make
RUN sudo make install

# Arguments for the source code repo for ONNXRuntime
ARG CODE_REPO=direbearform
ARG CODE_BRANCH=direbearform/direbearform/arm64jetson

# Set up build args
ARG BUILDTYPE=RelWithDebInfo
ARG BUILDARGS="--config ${BUILDTYPE} --arm64"

# Prepare onnxruntime Repo
WORKDIR /code
RUN git clone --single-branch --branch ${CODE_BRANCH} --recursive https://github.com/${CODE_REPO}/onnxruntime onnxruntime

# Build TRT enabled version
WORKDIR /code/onnxruntime
ENV CUDACXX=/usr/local/cuda/bin/nvcc
RUN ./build.sh ${BUILDARGS} --update --build \
    --use_cuda \
    --cudnn_home /usr/local/cuda \
    --cuda_home /usr/local/cuda \
    --use_tensorrt \
    --tensorrt_home /usr/src/tensorrt \
    --build_shared_lib \
    --enable_pybind --build_wheel

# ---- Stage final built ONNXRuntime wheel ----
RUN mkdir -p /dist && cp /code/onnxruntime/build/Linux/${BUILDTYPE}/dist/*.whl /dist/
RUN ls -l /dist