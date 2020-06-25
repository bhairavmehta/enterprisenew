# Notes about Kafka containers

The zookeeper/kafka base installation scripts are adopted from:
https://github.com/wurstmeister/zookeeper-docker
https://github.com/wurstmeister/kafka-docker

A public fork contains the necessary changes needed for cross-compilation and a different base suitable for ARM:
https://github.com/direbearform/zookeeper-docker
https://github.com/direbearform/kafka-docker

The base OpenJDK image for ARM32v7 is from:
https://www.balena.io/docs/reference/base-images/base-images-ref/.
The main reason to use Balena images is that their OpenJDK contains the Client mode libraries, where as Docker official OpenJDK images contains only Zero mode libraries.
