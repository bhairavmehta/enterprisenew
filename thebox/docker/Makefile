#!make

# ----------------
# Make Parameters
# ----------------

# Include locally set variables
include $(CURDIR)/env.private
export $(shell sed 's/=.*//' env.private)
export DOCKER_ADD_FLAGS ?= --squash

# Additional parameters
DIST_ORCHESTRATOR=../services/dist/thebox_orchestrator-0.1-py3-none-any.whl
DIST_INFERENCE=../services/dist/thebox_inference-0.1-py3-none-any.whl
DIST_NOTIFICATION=../services/dist/thebox_notification-0.1-py3-none-any.whl

# ----------------
# END: Make Parameters
# ----------------

# Constants (don't tweak)

ifeq ($(OS),Windows_NT)
#Windows stuff
NULL_DEV = nul
else
#Linux stuff
NULL_DEV = /dev/null
endif

ifeq ($(OS),Windows_NT)
CP_CMD=cp
RM_CMD=rm
WINVER?=$(shell powershell (Get-ComputerInfo).WindowsVersion)
else
CP_CMD=cp
RM_CMD=rm
endif

ifeq ($(OS),Windows_NT)
CHECKSUM_PACKAGELIST_BASE:=$(shell checksum -f="./base/PythonPackageList.txt" -t=sha256")
CHECKSUM_PACKAGELIST_INFERENCE_BASE:=$(shell checksum -f="./inference/base/PythonPackageList.txt" -t=sha256")
CHECKSUM_PACKAGELIST_INFERENCE_BASE_ARM64V8:=$(shell checksum -f="./inference/base_arm64v8/PythonPackageList.txt" -t=sha256")
CHECKSUM_PACKAGELIST_ORCHESTRATOR:=$(shell checksum -f="./orchestrator/PythonPackageList.txt" -t=sha256")
else
CHECKSUM_PACKAGELIST_BASE:=$(shell sha256sum ./base/PythonPackageList.txt | awk '{ print $$1 }')
CHECKSUM_PACKAGELIST_INFERENCE_BASE:=$(shell sha256sum ./inference/base/PythonPackageList.txt | awk '{ print $$1 }')
CHECKSUM_PACKAGELIST_INFERENCE_BASE_ARM64V8:=$(shell sha256sum ./inference/base_arm64v8/PythonPackageList.txt | awk '{ print $$1 }')
CHECKSUM_PACKAGELIST_ORCHESTRATOR:=$(shell sha256sum ./orchestrator/PythonPackageList.txt | awk '{ print $$1 }')
endif


all: packages packages-checksum x86

windows: packages packages-checksum x86_windows

prod: packages packages-checksum arm

ifeq ("${DOCKER_REGISTRY}", "")
push_debug: push_prep_failed
push_prod: push_prep_failed
else
push_debug: push_prep push_x86 push_kafka_x86
push_prod: push_prep push_arm push_kafka
endif

ifeq ("${DOCKER_REGISTRY_BASE_IMAGES}", "")
push_base: push_prep_failed
else
push_base: push_prep push_base_arm
endif

packages:
	$(info Rebuilding service packages ...)
	$(MAKE) -C $(CURDIR)/../services

	$(info Copy built packages packages ...)
	$(CP_CMD) $(DIST_ORCHESTRATOR) ./orchestrator/thebox_orchestrator-latest-py3-none-any.whl
	$(CP_CMD) $(DIST_INFERENCE) ./inference/inference/thebox_inference-latest-py3-none-any.whl
	$(CP_CMD) $(DIST_NOTIFICATION) ./notification/thebox_notification-latest-py3-none-any.whl

packages-checksum:
	$(info Creating Checksums for the built packages ...)
ifeq ($(OS),Windows_NT)
	$(eval CHECKSUM_DIST_ORCHESTRATOR:=$(shell checksum -f="${DIST_ORCHESTRATOR}" -t=sha256"))
	$(eval CHECKSUM_DIST_INFERENCE:=$(shell checksum -f="${DIST_INFERENCE}" -t=sha256"))
	$(eval CHECKSUM_DIST_NOTIFICATION:=$(shell checksum -f="${DIST_NOTIFICATION}" -t=sha256"))
else
	$(eval CHECKSUM_DIST_ORCHESTRATOR:=$(shell sha256sum ${DIST_ORCHESTRATOR} | awk '{ print $$1 }'))
	$(eval CHECKSUM_DIST_INFERENCE:=$(shell sha256sum ${DIST_INFERENCE} | awk '{ print $$1 }'))
	$(eval CHECKSUM_DIST_NOTIFICATION:=$(shell sha256sum ${DIST_NOTIFICATION} | awk '{ print $$1 }'))
endif

x86:
	$(MAKE) -C $(CURDIR)/kafka x86

	$(CP_CMD) ./scripts/wait-for-deps.sh ./base/wait-for-deps.sh.temp
	docker build -t amd64/thebox_base $(DOCKER_ADD_FLAGS) --build-arg IMAGE_ARCH=amd64 --build-arg IMAGE_ARCH_QEMU=x86_64 --build-arg CHECKSUM_PACKAGELIST=$(CHECKSUM_PACKAGELIST_BASE) ./base
	$(RM_CMD) ./base/wait-for-deps.sh.temp
	
	$(CP_CMD) ../services/workaround.py ./orchestrator/
	docker build -t amd64/thebox_orchestrator $(DOCKER_ADD_FLAGS) --build-arg IMAGE_ARCH=amd64 --build-arg CHECKSUM_PACKAGELIST=$(CHECKSUM_PACKAGELIST_ORCHESTRATOR) --build-arg DIST_FILE_CHECKSUM=$(CHECKSUM_DIST_ORCHESTRATOR) ./orchestrator
	$(RM_CMD) ./orchestrator/workaround.py

	docker build -t amd64/thebox_inference_base $(DOCKER_ADD_FLAGS) --build-arg IMAGE_ARCH=amd64 --build-arg CHECKSUM_PACKAGELIST=$(CHECKSUM_PACKAGELIST_INFERENCE_BASE) ./inference/base
	docker build -t amd64/thebox_inference $(DOCKER_ADD_FLAGS) --build-arg IMAGE_ARCH=amd64 --build-arg DIST_FILE_CHECKSUM=$(CHECKSUM_DIST_INFERENCE) ./inference/inference

	docker build -t amd64/thebox_notification $(DOCKER_ADD_FLAGS) --build-arg IMAGE_ARCH=amd64 --build-arg DIST_FILE_CHECKSUM=$(CHECKSUM_DIST_NOTIFICATION) ./notification

x86_windows:
	$(MAKE) -C $(CURDIR)/couchdb x86_windows
	$(MAKE) -C $(CURDIR)/kafka x86_windows

	$(CP_CMD) ./scripts/wait-for-it.psm1 ./base/wait-for-it.psm1.temp
	docker build -t amd64/thebox_base:windowscore $(DOCKER_ADD_FLAGS) --build-arg CHECKSUM_PACKAGELIST=$(CHECKSUM_PACKAGELIST_BASE) --build-arg WINVER=$(WINVER) -f ./base/Dockerfile.win ./base

	$(CP_CMD) ../services/workaround.py ./orchestrator/
	docker build -t amd64/thebox_orchestrator:windowscore $(DOCKER_ADD_FLAGS) --build-arg CHECKSUM_PACKAGELIST=$(CHECKSUM_PACKAGELIST_ORCHESTRATOR) --build-arg DIST_FILE_CHECKSUM=$(CHECKSUM_DIST_ORCHESTRATOR) --build-arg WINVER=$(WINVER) -f ./orchestrator/Dockerfile.win ./orchestrator
	$(RM_CMD) ./orchestrator/workaround.py

	docker build -t amd64/thebox_inference_base:windowscore $(DOCKER_ADD_FLAGS) --build-arg CHECKSUM_PACKAGELIST=$(CHECKSUM_PACKAGELIST_INFERENCE_BASE) --build-arg WINVER=$(WINVER) -f ./inference/base/Dockerfile.win ./inference/base
	docker build -t amd64/thebox_inference:windowscore $(DOCKER_ADD_FLAGS) --build-arg DIST_FILE_CHECKSUM=$(CHECKSUM_DIST_INFERENCE) --build-arg WINVER=$(WINVER) -f ./inference/inference/Dockerfile.win ./inference/inference

	docker build -t amd64/thebox_notification:windowscore $(DOCKER_ADD_FLAGS) --build-arg DIST_FILE_CHECKSUM=$(CHECKSUM_DIST_NOTIFICATION) --build-arg WINVER=$(WINVER) -f ./notification/Dockerfile.win ./notification
	
ifeq ("${DOCKER_REGISTRY_BASE_IMAGES}", "")
arm: arm_base arm_services
else
arm: arm_base_prebuilt arm_services
endif

arm_base:
	$(info Building TheBox base containers from scratch ...)

	$(MAKE) -C $(CURDIR)/kafka arm
	$(MAKE) -C $(CURDIR)/kafka arm64
	$(MAKE) -C $(CURDIR)/jetson

	$(CP_CMD) ./scripts/wait-for-deps.sh ./base/wait-for-deps.sh.temp
	docker build -t arm32v7/thebox_base $(DOCKER_ADD_FLAGS) --build-arg IMAGE_ARCH=arm32v7 --build-arg IMAGE_ARCH_QEMU=arm --build-arg CHECKSUM_PACKAGELIST=$(CHECKSUM_PACKAGELIST_BASE) ./base
	$(RM_CMD) ./base/wait-for-deps.sh.temp

	$(CP_CMD) ./scripts/wait-for-deps.sh ./inference/base_arm64v8/wait-for-deps.sh.temp
	docker build -t arm64v8/thebox_inference_base $(DOCKER_ADD_FLAGS) --build-arg IMAGE_ARCH=arm64v8 --build-arg CHECKSUM_PACKAGELIST=$(CHECKSUM_PACKAGELIST_INFERENCE_BASE_ARM64V8) ./inference/base_arm64v8

arm_base_prebuilt:
	$(eval DOCKER_REGISTRY_BASE_IMAGES_PREFIX = $(DOCKER_REGISTRY_BASE_IMAGES)/)
	$(info Skip building TheBox base containers and will pull from ${DOCKER_REGISTRY_BASE_IMAGES_PREFIX} ...)

arm_services:
	$(info Building TheBox service containers ...)

	$(CP_CMD) ../services/dist/thebox_orchestrator*.whl ./orchestrator/
	$(CP_CMD) ../services/workaround.py ./orchestrator/
	docker build -t arm32v7/thebox_orchestrator $(DOCKER_ADD_FLAGS) --build-arg IMAGE_REPO=$(DOCKER_REGISTRY_BASE_IMAGES_PREFIX) --build-arg IMAGE_ARCH=arm32v7 --build-arg DIST_FILE_CHECKSUM=$(CHECKSUM_DIST_ORCHESTRATOR) ./orchestrator
	$(RM_CMD) ./orchestrator/workaround.py

	$(CP_CMD) ../services/dist/thebox_inference*.whl ./inference/inference
	docker build -t arm64v8/thebox_inference $(DOCKER_ADD_FLAGS) --build-arg IMAGE_REPO=$(DOCKER_REGISTRY_BASE_IMAGES_PREFIX) --build-arg IMAGE_ARCH=arm64v8 --build-arg DIST_FILE_CHECKSUM=$(CHECKSUM_DIST_INFERENCE) ./inference/inference

	$(CP_CMD) ../services/dist/thebox_notification*.whl ./notification/
	docker build -t arm32v7/thebox_notification $(DOCKER_ADD_FLAGS) --build-arg IMAGE_REPO=$(DOCKER_REGISTRY_BASE_IMAGES_PREFIX) --build-arg IMAGE_ARCH=arm32v7 --build-arg DIST_FILE_CHECKSUM=$(CHECKSUM_DIST_NOTIFICATION) ./notification

push_prep:
	$(info DOCKER_REGISTRY = '${DOCKER_REGISTRY}')
	$(info DOCKER_REGISTRY_BASE_IMAGES = '${DOCKER_REGISTRY_BASE_IMAGES}')

push_prep_failed:
	$(error Must set a registry to push to. If needed, also need to modify /etc/docker/daemon.json to allow insecure registry)

push_x86:
	$(info Pusing all service containers (debug x86 version) to ${DOCKER_REGISTRY} ... )
	docker tag amd64/thebox_orchestrator ${DOCKER_REGISTRY}/amd64/thebox_orchestrator
	docker push ${DOCKER_REGISTRY}/amd64/thebox_orchestrator
	docker tag amd64/thebox_inference ${DOCKER_REGISTRY}/amd64/thebox_inference
	docker push ${DOCKER_REGISTRY}/amd64/thebox_inference
	docker tag amd64/thebox_notification ${DOCKER_REGISTRY}/amd64/thebox_notification
	docker push ${DOCKER_REGISTRY}/amd64/thebox_notification

push_base_arm:
	$(info Pusing all base containers (prod arm/arm64 version) to ${DOCKER_REGISTRY_BASE_IMAGES} ... )
	docker tag arm32v7/thebox_base ${DOCKER_REGISTRY_BASE_IMAGES}/arm32v7/thebox_base
	docker push ${DOCKER_REGISTRY_BASE_IMAGES}/arm32v7/thebox_base
	docker tag arm64v8/thebox_inference_base ${DOCKER_REGISTRY_BASE_IMAGES}/arm64v8/thebox_inference_base
	docker push ${DOCKER_REGISTRY_BASE_IMAGES}/arm64v8/thebox_inference_base

push_arm:
	$(info Pusing all service containers (prod arm/arm64 version) to ${DOCKER_REGISTRY} ... )
	docker tag arm32v7/thebox_orchestrator ${DOCKER_REGISTRY}/arm32v7/thebox_orchestrator
	docker push ${DOCKER_REGISTRY}/arm32v7/thebox_orchestrator
	docker tag arm64v8/thebox_inference ${DOCKER_REGISTRY}/arm64v8/thebox_inference
	docker push ${DOCKER_REGISTRY}/arm64v8/thebox_inference
	docker tag arm32v7/thebox_notification ${DOCKER_REGISTRY}/arm32v7/thebox_notification
	docker push ${DOCKER_REGISTRY}/arm32v7/thebox_notification

push_kafka:
	cd kafka && $(MAKE) DOCKER_REGISTRY=${DOCKER_REGISTRY} push_prod

push_kafka_x86:
	cd kafka && $(MAKE) DOCKER_REGISTRY=${DOCKER_REGISTRY} push_debug
