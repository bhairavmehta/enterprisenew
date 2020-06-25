#!make

# Inherited parameters from parent Make
# DOCKER_ADD_FLAGS

ifeq ($(OS),Windows_NT)
	#Windows stuff
	NULL_DEV = nul
else
	#Linux stuff
	NULL_DEV = /dev/null
endif

all: arm64deps arm64

arm64deps:

ifeq ("$(shell docker images -q amd64/jetpack_deps_1 2>$(NULL_DEV))", "")
	$(info Building NVIDIA SDK dependencies container image ...)
	docker build -t amd64/jetpack_deps --build-arg NV_USER=$(NV_USER) --build-arg VERSION_ID=18.04 ./deps
	docker stop jetpack_deps_1 || exit 0
	docker rm jetpack_deps_1 || exit 0
	docker run -it --name=jetpack_deps_1 amd64/jetpack_deps
	docker commit jetpack_deps_1 amd64/jetpack_deps_1
endif

arm64:
	$(info Building JetPack base images ...)
	docker build -t arm64v8/thebox_jetsonnano_base $(DOCKER_ADD_FLAGS) ./base
	docker build -t arm64v8/thebox_jetsonnano_rt $(DOCKER_ADD_FLAGS) --build-arg JETPACK_DEPENDENCIES_IMAGE=amd64/jetpack_deps_1 ./rt
	docker build -t arm64v8/thebox_jetsonnano_dev $(DOCKER_ADD_FLAGS) --build-arg JETPACK_DEPENDENCIES_IMAGE=amd64/jetpack_deps_1 ./dev
	docker build -t arm64v8/thebox_jetsonnano_onnxrt $(DOCKER_ADD_FLAGS) ./onnxrt
