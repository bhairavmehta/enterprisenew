#!make

# A K8s powered 'The Box' has following network topology
#
#                               +--> [ Node1 ]
#                               |
#   (User/App) --> [ Router ] --+--> [ Node2 ]
#                               |
#                               +--> [ Node3 ]
#
# The NAT subnet inside the router has internally allocated address.
# The router has an external facing DHCP allocated IP and a hostname
# K8s cluster exposed service/node ports are exposed to outside
# by Router acting in NAT mode.

# Include locally set variables
include $(CURDIR)/k8senv.private
export $(shell sed 's/=.*//' k8senv.private)

# K8s schema files used for verification
# default to v1.13.5 (LKG for RPI)
SCHEMA_NAME=v1.13.5-standalone


ifeq ($(OS),Windows_NT)
# Windows
KUBERNETES_SCHEMA_FILE_ROOT=$(shell echo $(CURDIR)\temp\kubernetes-json-schema)
SCHEMA_FILE_PATH=$(KUBERNETES_SCHEMA_FILE_ROOT)\$(SCHEMA_NAME)
else
#Linux stuff
KUBERNETES_SCHEMA_FILE_ROOT=$(CURDIR)/temp/kubernetes-json-schema
SCHEMA_FILE_PATH=$(KUBERNETES_SCHEMA_FILE_ROOT)/$(SCHEMA_NAME)
endif


ifeq ("$(DOCKER_REGISTRY)", "")
$(error Must provide a valid DOCKER_REGISTRY value)
endif
ifeq ("$(KUBERNETES_CLUSTER_IP)", "")
$(error Must provide a valid KUBERNETES_CLUSTER_IP value)
endif
ifeq ("$(EXTERNAL_PUBSUB_ENDPOINT)", "")
$(error Must provide a valid EXTERNAL_PUBSUB_ENDPOINT value)
endif


all: build verify

build:

ifeq ($(OS),Windows_NT)
# Windows

	sed -e "s@\$${DOCKER_REGISTRY}@$(DOCKER_REGISTRY)@" \
		-e "s@\$${KUBERNETES_CLUSTER_IP}@$(KUBERNETES_CLUSTER_IP)@" \
		-e "s@\$${EXTERNAL_PUBSUB_ENDPOINT}@$(EXTERNAL_PUBSUB_ENDPOINT)@" \
		thebox.template.yml \
		> thebox.yml.tmp

	sed -e "s@\$${STORAGE_SERVER}@$(STORAGE_SERVER)@" \
		-e "s@\$${STORAGE_SERVER_PATH}@$(STORAGE_SERVER_PATH)@" \
		thebox_storage.template.yml \
		> thebox_storage.yml.tmp
else
#Linux stuff

	sed -e 's@\$${DOCKER_REGISTRY}@$(DOCKER_REGISTRY)@' \
		-e 's@\$${KUBERNETES_CLUSTER_IP}@$(KUBERNETES_CLUSTER_IP)@' \
		-e 's@\$${EXTERNAL_PUBSUB_ENDPOINT}@$(EXTERNAL_PUBSUB_ENDPOINT)@' \
		thebox.template.yml \
		> thebox.yml.tmp

	sed -e 's@\$${STORAGE_SERVER}@$(STORAGE_SERVER)@' \
		-e 's@\$${STORAGE_SERVER_PATH}@$(STORAGE_SERVER_PATH)@' \
		thebox_storage.template.yml \
		> thebox_storage.yml.tmp
endif

# verify schemas
# See: https://github.com/garethr/kubernetes-json-schema
ifeq ("$(wildcard $(SCHEMA_FILE_PATH))", "")
	
	$(info Schema file path does not exist: $(SCHEMA_FILE_PATH), trying to install ...)
	pip install yq jsonschema
	mkdir -p temp
	cd temp && git clone https://github.com/garethr/kubernetes-json-schema

endif

verify:
	cat thebox.yml.tmp | yq . | jq -c . > thebox.json.tmp
	python validate_k8s.py --json thebox.json.tmp --schema $(SCHEMA_FILE_PATH)

	cat thebox_storage.yml.tmp | yq . | jq -c . > thebox_storage.json.tmp
	python validate_k8s.py --json thebox_storage.json.tmp --schema $(SCHEMA_FILE_PATH)
