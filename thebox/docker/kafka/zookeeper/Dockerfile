ARG IMAGE

# ----- Base image to get QEMU binaries -----
FROM debian:buster
RUN apt-get update && apt-get install -qqy qemu-user-static

# ----- Acutual image base for Zookeeper with JRE/Debian -----
FROM ${IMAGE}

# ----- Copy over QEMU ----
COPY --from=0 /usr/bin/qemu-aarch64-static /usr/bin/qemu-aarch64-static
COPY --from=0 /usr/bin/qemu-arm-static /usr/bin/qemu-arm-static

LABEL maintainer="Wurstmeister"

ARG ZOOKEEPER_VERSION=3.4.14

RUN apt-get update && apt-get install -y --no-install-recommends apt-transport-https ca-certificates wget software-properties-common

#Download Zookeeper
RUN wget -q https://www.apache.org/dist/zookeeper/zookeeper-${ZOOKEEPER_VERSION}/zookeeper-${ZOOKEEPER_VERSION}.tar.gz && \
  wget -q https://www.apache.org/dist/zookeeper/KEYS && \
  wget -q https://www.apache.org/dist/zookeeper/zookeeper-${ZOOKEEPER_VERSION}/zookeeper-${ZOOKEEPER_VERSION}.tar.gz.asc && \
  wget -q https://www.apache.org/dist/zookeeper/zookeeper-${ZOOKEEPER_VERSION}/zookeeper-${ZOOKEEPER_VERSION}.tar.gz.sha512

#Verify download
RUN sha512sum -c zookeeper-${ZOOKEEPER_VERSION}.tar.gz.sha512 && \
  gpg --import KEYS && \
  gpg --verify zookeeper-${ZOOKEEPER_VERSION}.tar.gz.asc

#Install
RUN tar -xzf zookeeper-${ZOOKEEPER_VERSION}.tar.gz -C /opt

#Configure
RUN mv /opt/zookeeper-${ZOOKEEPER_VERSION}/conf/zoo_sample.cfg /opt/zookeeper-${ZOOKEEPER_VERSION}/conf/zoo.cfg

ENV ZK_HOME /opt/zookeeper-${ZOOKEEPER_VERSION}
RUN sed  -i "s|/tmp/zookeeper|$ZK_HOME/data|g" $ZK_HOME/conf/zoo.cfg; mkdir $ZK_HOME/data
RUN apt-get install dos2unix
ADD start-zk.sh /usr/bin/start-zk.sh
RUN dos2unix /usr/bin/start-zk.sh
EXPOSE 2181 2888 3888

WORKDIR /opt/zookeeper-${ZOOKEEPER_VERSION}
VOLUME ["/opt/zookeeper-${ZOOKEEPER_VERSION}/conf", "/opt/zookeeper-${ZOOKEEPER_VERSION}/data"]

CMD ["/bin/bash", "/usr/bin/start-zk.sh", "start"]
