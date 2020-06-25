# Image hosting the files to JetPack
ARG JETPACK_DEPENDENCIES_IMAGE
FROM ${JETPACK_DEPENDENCIES_IMAGE} AS dep

# Real base image
FROM arm64v8/thebox_jetsonnano_base

# Prereqs
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  gnupg \
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# ----- Install CUDA support libraries
ARG CUDA_MAJOR_VERSION=10
ARG CUDA_MAJOR_REVISION=0
ARG CUDA_MINOR_VERSION=326_1.0
ARG JETPACK_VERSION=4.2.2

# ----- Install CUDA support libraries
ENV CUDA_VERSION_FULL=${CUDA_MAJOR_VERSION}.${CUDA_MAJOR_REVISION}.${CUDA_MINOR_VERSION}
ENV CUDA_VERSION_DASH=${CUDA_MAJOR_VERSION}-${CUDA_MAJOR_REVISION}
ENV CUDA_PKG_VERSION=${CUDA_VERSION_FULL}-1
ENV CUDA_TOOLKIT_PKG="cuda-repo-l4t-${CUDA_VERSION_DASH}-local-${CUDA_PKG_VERSION}_arm64.deb"

# Lay down cuda-repo-l4t locally and install the required runtimes
COPY --from=dep /tmp/GA_${JETPACK_VERSION}/P3448-0000/${CUDA_TOOLKIT_PKG} /tmp
RUN dpkg --force-all -i /tmp/${CUDA_TOOLKIT_PKG} && \
  rm /tmp/${CUDA_TOOLKIT_PKG} \
  && \
  apt-key add /var/cuda-repo-*-local*/*.pub && \
  apt-get update && \
  apt-get install -y --no-install-recommends --allow-downgrades \
  cuda-cudart-${CUDA_VERSION_DASH} \
  cuda-nvtx-${CUDA_VERSION_DASH} \
  cuda-cublas-${CUDA_VERSION_DASH} \
  cuda-cufft-${CUDA_VERSION_DASH} \
  cuda-curand-${CUDA_VERSION_DASH} \
  cuda-cusolver-${CUDA_VERSION_DASH} \
  cuda-license-${CUDA_VERSION_DASH} \
  cuda-nvrtc-${CUDA_VERSION_DASH} \
  cuda-cusparse-${CUDA_VERSION_DASH} \
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* \
  && \
  export CUDA_PKG_NAME="$(echo $CUDA_PKG_VERSION | sed 's/_.*$//')" && \
  dpkg --purge cuda-repo-l4t-${CUDA_VERSION_DASH}-local-${CUDA_PKG_NAME} && \
  ln -s /usr/local/cuda-${CUDA_MAJOR_VERSION}.${CUDA_MAJOR_REVISION} /usr/local/cuda

RUN grep -q "export PATH=.*/usr/local/cuda/bin" ~/.bashrc || echo "export PATH=/usr/local/cuda/bin:$PATH">>~/.bashrc && \
  grep -q "export LD_LIBRARY_PATH=/usr/local/cuda/lib64" ~/.bashrc || echo "export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH" >> ~/.bashrc && \
  export LD_LIBRARY_PATH=/usr/local/cuda/lib64:${LD_LIBRARY_PATH}

# ---- Putting in some metadata
LABEL com.nvidia.jetpack.version="${JETPACK_VERSION}"
LABEL com.nvidia.cuda.version="${CUDA_VERSION_FULL}"

# ----- Install CUDA enabled opencv
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  libavcodec57 \
  libavformat57  \
  libavutil55  \
  libcairo2  \
  libgdk-pixbuf2.0-0  \
  libglib2.0-0  \
  libgstreamer-plugins-base1.0-0  \
  libgstreamer1.0-0  \
  libgtk2.0-0  \
  libjpeg8  \
  libpng16-16  \
  libswscale4  \
  libtbb2 \
  libtiff5 \
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

ARG OPENCV_VERSION=3.3.1-2-g31ccdfe11

ENV OPENCV_PKG="libopencv_${OPENCV_VERSION}_arm64.deb"
ENV OPENCV_PYTHON_PKG="libopencv-python_${OPENCV_VERSION}_arm64.deb"

COPY --from=dep /tmp/GA_${JETPACK_VERSION}/P3448-0000/${OPENCV_PKG} /tmp
COPY --from=dep /tmp/GA_${JETPACK_VERSION}/P3448-0000/${OPENCV_PYTHON_PKG} /tmp

RUN apt install -y --no-install-recommends /tmp/${OPENCV_PKG} && \
  apt install -y --no-install-recommends /tmp/${OPENCV_PYTHON_PKG} && \
  rm /tmp/${OPENCV_PKG} && \
  rm /tmp/${OPENCV_PYTHON_PKG} && \
  apt-get clean


# ----- Install CU-DNN, NVInfer etc. required by TensorRT and TensorRT itself
ENV CUDNN_PKG="libcudnn7_7.5.0.56-1+cuda${CUDA_MAJOR_VERSION}.${CUDA_MAJOR_REVISION}_arm64.deb"
ENV NVINFER="libnvinfer5_5.1.6-1+cuda${CUDA_MAJOR_VERSION}.${CUDA_MAJOR_REVISION}_arm64.deb"
#ENV TENSORRT="tensorrt_5.0.6.3-1+cuda${CUDA_MAJOR_VERSION}.${CUDA_MAJOR_REVISION}_arm64.deb"

COPY --from=dep /tmp/GA_${JETPACK_VERSION}/P3448-0000/${CUDNN_PKG} /tmp
COPY --from=dep /tmp/GA_${JETPACK_VERSION}/P3448-0000/${NVINFER} /tmp
#COPY --from=dep /tmp/GA_${JETPACK_VERSION}/P3448-0000/${TENSORRT} /tmp

RUN apt install -y --no-install-recommends /tmp/${CUDNN_PKG} && \
  apt install -y --no-install-recommends /tmp/${NVINFER} && \
  #apt install -y --no-install-recommends /tmp/${TENSORRT} && \
  rm /tmp/${CUDNN_PKG} && \
  rm /tmp/${NVINFER} && \
  #rm /tmp/${TENSORRT} && \
  apt-get clean
