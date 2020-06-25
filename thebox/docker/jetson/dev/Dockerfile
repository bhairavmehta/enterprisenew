ARG JETPACK_DEPENDENCIES_IMAGE

# Set the architecture base
FROM arm64v8/thebox_jetsonnano_rt

# Image hosting the files to JetPack
FROM ${JETPACK_DEPENDENCIES_IMAGE} AS dep

# Real base image
FROM arm64v8/thebox_jetsonnano_rt

# ----- Install CUDA support libraries
ARG CUDA_MAJOR_VERSION=10
ARG CUDA_MAJOR_REVISION=0
ARG CUDA_MINOR_VERSION=326_1.0
ARG OPENCV_VERSION=3.3.1-2-g31ccdfe11
ARG JETPACK_VERSION=4.2.2

# ---- Install CUDA dev bits
ENV CUDA_VERSION_FULL=${CUDA_MAJOR_VERSION}.${CUDA_MAJOR_REVISION}.${CUDA_MINOR_VERSION}
ENV CUDA_VERSION_DASH=${CUDA_MAJOR_VERSION}-${CUDA_MAJOR_REVISION}
ENV CUDA_PKG_VERSION=${CUDA_VERSION_FULL}-1
ENV CUDA_TOOLKIT_PKG="cuda-repo-l4t-${CUDA_VERSION_DASH}-local-${CUDA_PKG_VERSION}_arm64.deb"

COPY --from=dep /tmp/GA_${JETPACK_VERSION}/P3448-0000/${CUDA_TOOLKIT_PKG} /tmp
RUN dpkg --force-all -i /tmp/${CUDA_TOOLKIT_PKG} && \
  rm /tmp/${CUDA_TOOLKIT_PKG} \
  && \
  apt-key add /var/cuda-repo-*-local*/*.pub && \
  apt-get update && \
  apt-get install -y --no-install-recommends --allow-downgrades \
  cuda-nvcc-10-0 \
  cuda-libraries-dev-10-0 \
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* \
  && \
  export CUDA_PKG_NAME="$(echo $CUDA_PKG_VERSION | sed 's/_.*$//')" && \
  dpkg --purge cuda-repo-l4t-10-0-local-${CUDA_PKG_NAME}

RUN apt-get update && apt-get install -y --no-install-recommends \
  libtbb-dev \
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# ----- Install DEV packages that are not part of cuda tool kits
ENV CUDNN_DEV="libcudnn7-dev_7.5.0.56-1+cuda${CUDA_MAJOR_VERSION}.${CUDA_MAJOR_REVISION}_arm64.deb"
ENV NVINFER_DEV="libnvinfer-dev_5.1.6-1+cuda${CUDA_MAJOR_VERSION}.${CUDA_MAJOR_REVISION}_arm64.deb"
ENV OPENCV_DEV_PKG="libopencv-dev_${OPENCV_VERSION}_arm64.deb"
#ENV OPENCV_PYTHON_PKG="libopencv-python_${OPENCV_VERSION}_arm64.deb"
#ENV OPENCV_SAMPLES_PKG="libopencv-samples_${OPENCV_VERSION}_arm64.deb"

COPY --from=dep /tmp/GA_${JETPACK_VERSION}/P3448-0000/${CUDNN_DEV} /tmp
COPY --from=dep /tmp/GA_${JETPACK_VERSION}/P3448-0000/${NVINFER_DEV} /tmp
COPY --from=dep /tmp/GA_${JETPACK_VERSION}/P3448-0000/${OPENCV_DEV_PKG} /tmp
#COPY --from=dep /tmp/GA_${JETPACK_VERSION}/P3448-0000/${OPENCV_PYTHON_PKG} /tmp
#COPY --from=dep /tmp/GA_${JETPACK_VERSION}/P3448-0000/${OPENCV_SAMPLES_PKG} /tmp

RUN apt install -y --no-install-recommends /tmp/${CUDNN_DEV} && \
  apt install -y --no-install-recommends /tmp/${NVINFER_DEV} && \
  apt install -y --no-install-recommends /tmp/${OPENCV_DEV_PKG} && \
  #apt install -y --no-install-recommends /tmp/${OPENCV_PYTHON_PKG} && \
  #apt install -y --no-install-recommends /tmp/${OPENCV_SAMPLES_PKG} && \
  rm /tmp/${CUDNN_DEV} && \
  rm /tmp/${NVINFER_DEV} && \
  rm /tmp/${OPENCV_DEV_PKG} && \
  #rm /tmp/${OPENCV_PYTHON_PKG} && \
  #rm /tmp/${OPENCV_SAMPLES_PKG} && \
  apt-get clean

# ----- Install Compiler tools -----
RUN apt-get update && apt-get install -y --no-install-recommends \
  apt-transport-https \
  build-essential \
  gfortran \
  ca-certificates \
  cmake \
  curl \
  git \
  libatlas-base-dev \
  libcurl4-openssl-dev \
  libjemalloc-dev \
  liblapack-dev \
  libopenblas-dev \
  libzmq3-dev \
  ninja-build \
  python-dev \
  python3-dev \
  software-properties-common \
  unzip \
  virtualenv \
  wget \
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*
