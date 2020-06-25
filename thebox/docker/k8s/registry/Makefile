#!make


ifeq ($(OS),Windows_NT)
#Windows stuff
LOCAL_REGISTRY_STORE_PATH:=$(shell echo $(USERPROFILE)/docker_registry| sed "s@\\@/@g")
LOCAL_REGISTRY_STORE_PATH_WIN:=$(shell echo $(LOCAL_REGISTRY_STORE_PATH)| sed "s@/@\\@g")
else
#Linux stuff
LOCAL_REGISTRY_STORE_PATH=$(HOME)/docker_registry
endif



# Supported values:
# x86: latest
# arm: arm32v7-static
# arm64: arm64v8-static
REGISTRY_UI_IMAGE_TAG=latest

HOSTNAME:=$(hostname).local


all:
#mkdir -p $(LOCAL_REGISTRY_STORE_PATH)

ifeq ($(OS),Windows_NT)
# Windows
ifeq ("$(wildcard $(LOCAL_REGISTRY_STORE_PATH_WIN))", "")
		mkdir -p $(LOCAL_REGISTRY_STORE_PATH_WIN)
endif
		sed -e "s@\$${LOCAL_REGISTRY_STORE_PATH}@$(LOCAL_REGISTRY_STORE_PATH)@" \
		    -e "s@\$${REGISTRY_UI_IMAGE_TAG}@$(REGISTRY_UI_IMAGE_TAG)@" \
				docker_registry.template.yml \
				> docker_registry.yml.tmp

else
#Linux stuff
		mkdir -p $(LOCAL_REGISTRY_STORE_PATH)
		sed -e 's@\$${LOCAL_REGISTRY_STORE_PATH}@$(LOCAL_REGISTRY_STORE_PATH)@' \
		    -e 's@\$${REGISTRY_UI_IMAGE_TAG}@$(REGISTRY_UI_IMAGE_TAG)@' \
				docker_registry.template.yml \
				> docker_registry.yml.tmp
		
endif

		docker-compose -f docker_registry.yml.tmp up -d
