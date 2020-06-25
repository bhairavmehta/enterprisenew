#!make

ifeq ($(OS),Windows_NT)
WINVER?=$(shell powershell (Get-ComputerInfo).WindowsVersion)
endif

all: windows

windows: x86_windows

x86_windows:
		docker build -t couchdb:windowscore $(DOCKER_ADD_FLAGS) --build-arg WINVER=$(WINVER) -f Dockerfile.win ./


