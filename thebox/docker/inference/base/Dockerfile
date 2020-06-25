# IMAGE_ARCH Possible choices:
#  - amd64 (for x86 Windows or Linux)
ARG IMAGE_ARCH="amd64"
FROM ${IMAGE_ARCH}/thebox_base

# ---- Install requirements for the inference containers ----
ARG CHECKSUM_PACKAGELIST
RUN mkdir -p /tmp
COPY PythonPackageList.txt /tmp
RUN pip install -r /tmp/PythonPackageList.txt -v

