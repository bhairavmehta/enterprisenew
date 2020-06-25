@echo off

REM This script must be run as admin

systeminfo | grep "Hyper-V Requirements"

IF %errorlevel% NEQ 0 (
    echo You must install Hyper-V first
    exit /b 1
)

choco install minikube kubernetes-cli

minikube config set memory 4096
minikube config set cpus 2
minikube config set vm-driver hyperv

REM To start minikube with Hyper-V driver, first, create a new external
REM switch. Assume you name it 'MinikubeVS', then do:
REM minikube config set hyperv-virtual-switch MinikubeVS

REM TO Start Minikube:
REM   minikube start --insecure-registry <your_private_docker_registry>
REM
REM e.g. in WSL2 setup, one first have to expose the registry to the host
REM using NAT to some port, say 5000, then the registry would be:
REM   minikube start --insecure-registry <host_fqdn>:5000
REM
REM to find out host FQDN, do:
REM   ping -a localhost



REM To Stop Minikube:
REM   minikube stop


REM To delete the cluster
REM   minikube delete

REM To login into minibkue's VM:
REM see: https://github.com/boot2docker/boot2docker#ssh-into-vm
REM  user: docker
REM  pass: tcuser