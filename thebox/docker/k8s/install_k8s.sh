#!/bin/bash

# Currently doesn't run in WSL1/2 yet due to lack of VM virtualization feature
if [ "$(egrep --color 'vmx|svm' /proc/cpuinfo)" == "" ]; then
    echo "You must run this in a virualization capable environment"
    exit 1
fi

# Install KVM2
sudo apt install libvirt-clients libvirt-daemon-system qemu-kvm
sudo systemctl enable libvirtd.service
sudo systemctl start libvirtd.service
sudo usermod -a -G libvirt $(whoami)
newgrp libvirt

# Install minikube
curl -Lo minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 \
  && chmod +x minikube
sudo install minikube /usr/local/bin
rm minikube
minikube config set memory 4096
minikube config set cpus 2

# Install KVM2 driver
curl -LO https://storage.googleapis.com/minikube/releases/latest/docker-machine-driver-kvm2 \
  && sudo install docker-machine-driver-kvm2 /usr/local/bin/
minikube config set vm-driver kvm2

# Install KubeCtl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add
echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt update
sudo apt install kubectl

# TO Start Minikube:
#
#   minikube start --insecure-registry <your_private_docker_registry>
#

# To Stop Minikube:
# minikube stop

# To delete the cluster
# minikube delete

# To login into minibkue's VM:
# see: https://github.com/boot2docker/boot2docker#ssh-into-vm
#  user: docker
#  pass: tcuser