# IMAGE_ARCH Possible choices:
#  - arm64v8 (for Jetson)
#  - arm32v7 (for raspbian)
#  - amd64 (for x86 Windows or Linux)
ARG IMAGE_REPO=""
ARG IMAGE_ARCH="amd64"
FROM ${IMAGE_REPO}${IMAGE_ARCH}/thebox_base

# ---- Deploy the app ----
ARG DIST_FILE_CHECKSUM
COPY thebox_notification-latest-py3-none-any.whl /tmp/
RUN echo ${DIST_FILE_CHECKSUM} /tmp/thebox_notification-latest-py3-none-any.whl > /tmp/checksum.txt && \
  sha256sum -c /tmp/checksum.txt && \
  pip install /tmp/thebox_notification-latest-py3-none-any.whl

# ---- Copy the default config as template ----
COPY config.default.yml /config.yml

# ---- Default start command ----
ENV SERVICE_DEPENDENCIES=
RUN apt-get update
RUN apt-get install dos2unix
RUN dos2unix /usr/bin/wait-for-deps.sh

RUN echo "if [ \"\$SERVICE_DEPENDENCIES\" != \"\" ]; then /usr/bin/wait-for-deps.sh \$SERVICE_DEPENDENCIES; fi && \
  python3 -m thebox.notification -c /config.yml" > /start.sh && \
  chmod 755 /start.sh

CMD ["/bin/bash", "-c", "/start.sh"]
