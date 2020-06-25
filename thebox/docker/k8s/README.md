# The Box - Kubernetes Deployment File

Generate a deployment file for deployment on real prototype H/W consist of Raspberry PIs and NVIDIA Jetson devices.

## Preparation

Clone the [kubernetes-json-schema](https://github.com/garethr/kubernetes-json-schema) locally:

```bash
git clone https://github.com/garethr/kubernetes-json-schema.git
```

## Build

Run 'make' with several mandatory parameters:

```batch
make KUBERNETES_SCHEMA_FILE_ROOT=[path_to_cloned_kubernetes_json_schema] DOCKER_REGISTRY=[hostname:port of docker registry] KUBERNETES_CLUSTER=[ip address of K8s cluster]
```

E.g.

```batch
make KUBERNETES_SCHEMA_FILE_ROOT=e:\GitHub\kubernetes-json-schema DOCKER_REGISTRY=thebox2-pi2:443 KUBERNETES_CLUSTER_IP=192.168.1.122
```

### Deploy

1. Upload the generated thebox.yml.tmp to the Kubernetes cluster master node

2. On the master node, do:

   ```bash
   kubectl apply -f thebox.yml.tmp
   ```
