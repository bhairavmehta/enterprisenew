# ---- Base image for compiling mxnet runtime
FROM arm64v8/thebox_jetsonnano_dev

# ---- Install additional dependencies ----
RUN apt-get update && apt-get install -y --no-install-recommends \
  libhdf5-dev \
  protobuf-compiler \
  libprotoc-dev \
  python3-numpy \
  # additional build related tools
  python3-pip \
  python3-setuptools \
  ccache \
  pkg-config \
  && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

# ---- Download MXNet source code -----
ARG MXNET_LKG_COMMIT
RUN cd /root && \
  git clone --recursive https://github.com/dmlc/mxnet && \
  cd /root/mxnet && \
  if [ "$MXNET_LKG_COMMIT" != "" ]; then git reset --hard $MXNET_LKG_COMMIT ; fi

# ---- Build ONNX ----
RUN cd /root/mxnet/3rdparty/onnx-tensorrt/third_party/onnx && \
  mkdir -p build && \
  cd build && \
  cmake \
  -DCMAKE_CXX_COMPILER_LAUNCHER=ccache \
  -DCMAKE_C_COMPILER_LAUNCHER=ccache \
  -DCMAKE_CXX_FLAGS=-I/usr/include/python3.6 \
  -DBUILD_SHARED_LIBS=ON ..\
  -G Ninja && \
  ninja -j $(nproc) -v onnx/onnx.proto && \
  ninja -j $(nproc) -v

# ---- Build ONNX-TensorRT ----
RUN cd /root/mxnet/3rdparty/onnx-tensorrt && \
  mkdir -p build && \
  cd build && \
  export CUDACXX=/usr/local/cuda/bin/nvcc && \
  cmake \
  -DCMAKE_CXX_COMPILER_LAUNCHER=ccache \
  -DCMAKE_C_COMPILER_LAUNCHER=ccache \
  -DCUDA_TOOLKIT_ROOT_DIR=/usr/local/cuda \
  -DCUDA_INCLUDE_DIRS=/usr/local/cuda/include \
  .. \
  && \
  make -j $(nproc)

# ---- Build MXNet with GPU support ----
RUN cd /root/mxnet && \
  make -j $(nproc) \
  USE_LAPACK=1 \
  USE_LAPACK_PATH=/usr/lib/aarch64-linux-gnu/lapack \
  USE_JEALLOC=1 \
  USE_JEMALLOC_PATH=/usr/lib/aarch64-linux-gnu \
  USE_OPENCV=1 \
  USE_BLAS=openblas \
  USE_CUDA=1 \
  ENABLE_CUDA_RTC=1 \
  USE_CUDNN=1 \
  USE_CUDA_PATH=/usr/local/cuda \
  USE_CPP_PACKAGE=0 \
  USE_F16C=0 \
  CUDA_ARCH="-gencode arch=compute_53,code=sm_53"

# ---- Build MXNet Python binding ----
RUN pip3 install wheel && \
  cd /root/mxnet/python && \
  python3 setup.py bdist_wheel

# ---- Final build output for MXNet Wheel ----
RUN mkdir -p /dist && cp /root/mxnet/python/dist/mxnet-*.whl /dist/
RUN ls -l /dist
