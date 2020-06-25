#!make

DOCKER_REGISTRY=

ifeq ($(OS),Windows_NT)
WINVER?=$(shell powershell (Get-ComputerInfo).WindowsVersion)
endif

all: x86 arm arm64

windows: x86_windows

ifeq ("${DOCKER_REGISTRY}", "")
push_debug: push_prep_failed
push_prod: push_prep_failed
else
push_debug: push_prep push_x86
push_prod: push_prep push_arm push_arm64
endif

x86:
		docker build -t amd64/thebox_zookeeper --build-arg IMAGE=amd64/openjdk:7-jre-jessie ./zookeeper
		docker build -t amd64/thebox_kafka --build-arg IMAGE=amd64/openjdk:8-jre-stretch ./kafka

x86_windows:
		docker build -t amd64/thebox_zookeeper:windowscore $(DOCKER_ADD_FLAGS) --build-arg WINVER=$(WINVER) -f ./zookeeper/Dockerfile.win ./zookeeper
		docker build -t amd64/thebox_kafka:windowscore $(DOCKER_ADD_FLAGS) --build-arg WINVER=$(WINVER) -f ./kafka/Dockerfile.win ./kafka

arm:
		docker build -t arm32v7/thebox_zookeeper --build-arg IMAGE=balenalib/armv7hf-openjdk:7-jessie ./zookeeper
		docker build -t arm32v7/thebox_kafka --build-arg IMAGE=balenalib/armv7hf-openjdk:8-stretch ./kafka

arm64:
		docker build -t arm64v8/thebox_zookeeper --build-arg IMAGE=balenalib/generic-aarch64-debian-openjdk:7-jessie ./zookeeper
		docker build -t arm64v8/thebox_kafka --build-arg IMAGE=balenalib/generic-aarch64-debian-openjdk:8-stretch ./kafka

push_prep:
		$(info Registry set to ${DOCKER_REGISTRY})

push_prep_failed:
		$(error Must set a DOCKER_REGISTRY to push to ${DOCKER_REGISTRY}. If needed, also need to modify /etc/docker/daemon.json to allow insecure registry)

push_arm:
		docker tag arm32v7/thebox_zookeeper ${DOCKER_REGISTRY}/arm32v7/thebox_zookeeper
		docker push ${DOCKER_REGISTRY}/arm32v7/thebox_zookeeper
		docker tag arm32v7/thebox_kafka ${DOCKER_REGISTRY}/arm32v7/thebox_kafka
		docker push ${DOCKER_REGISTRY}/arm32v7/thebox_kafka

push_arm64:
		docker tag arm64v8/thebox_zookeeper ${DOCKER_REGISTRY}/arm64v8/thebox_zookeeper
		docker push ${DOCKER_REGISTRY}/arm64v8/thebox_zookeeper
		docker tag arm64v8/thebox_kafka ${DOCKER_REGISTRY}/arm64v8/thebox_kafka
		docker push ${DOCKER_REGISTRY}/arm64v8/thebox_kafka

push_x86:
		docker tag amd64/thebox_zookeeper ${DOCKER_REGISTRY}/amd64/thebox_zookeeper
		docker push ${DOCKER_REGISTRY}/amd64/thebox_zookeeper
		docker tag amd64/thebox_kafka ${DOCKER_REGISTRY}/amd64/thebox_kafka
		docker push ${DOCKER_REGISTRY}/amd64/thebox_kafka
