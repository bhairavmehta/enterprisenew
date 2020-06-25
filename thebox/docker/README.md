# The Box - Services Containers

Both Linux containers and Windows containers are supported. Linux containers can be built on both Windows or Linux, while Windows containers can only be built on Windows with (Docker for Windows)[https://docs.docker.com/docker-for-windows/] or (Docker EE)[https://docs.docker.com/ee/docker-ee/windows/docker-ee/].

## Table of Content

- [Preparation](#preparation)
- [Building TheBox Service Containers (Linux Containers)](#building-thebox-service-containers-linux-containers)
- [Developing/debugging the services in x86 containers locally (Linux Containers)](#developingdebugging-the-services-in-x86-containers-locally-linux-containers)
- [Running x86 containers locally (Linux Containers, without debugging)](#running-x86-containers-locally-linux-containers-without-debugging)
- [Building ARM containers for running on the real prototype hardware (RPIs+JetsonNano):](#building-arm-containers-for-running-on-the-real-prototype-hardware-rpisjetsonnano)
- [Building TheBox Service Containers (Windows Containers)](#building-thebox-service-containers-windows-containers)
- [Running x86 containers locally (Windows Containers, without debugging)](#running-x86-containers-locally-windows-containers-without-debugging)

## Preparation

1. Please install Docker CE (or Docker for Windows if on Windows) or Docker EE.
2. Please refer to this [link](../services/README.md) for the preparation steps to be able to build 'The Box' services distributables. You will need to run make command in a Python virtual environment.
3. Please make a copy of env.template to env.private, and override any settings if needed. For example, to build smaller containers, please use follow flags (not on by default):
   ```bash
   # You may need to enable Docker's experimental features for above flag to work as of now.
   DOCKER_ADD_FLAGS=--squash
   ```
   Unless for building containers for the real prototype ARM (Linux) based H/W, the DOCKER_REGISTRY is not used and can be ignored, and you can proceed to build the containers.
4. (Optional) For building and deploying to real prototype ARM (Linux) H/W:
   1. Please make sure you have created a private docker registry to host the containers. Follow [this guide](DockerRegistry.md) on how to create a private registry.
   2. Once you have the registry, update env.private DOCKER_REGISTRY parameter to point to it, e.g., suppose it is myregistry.guest.corp.microsoft.com on port 5000:
      ```
      DOCKER_REGISTRY=myregistry.guest.corp.microsoft.com:5000
      ```
      If your registry is HTTP instead of HTTPS w/ valid cert, you may also need to add this private registry into the docker's daemon.json file:
      ```
      {
          ...
          "insecure-registries": ["myregistry.guest.corp.microsoft.com:5000"],
          ...
      }
      ```
   3. To build from scratch, you also need to register an NVIDIA devzone account and also download a copy of SDK Manager debian package manually. Please refer to this [link](jetson/README.md)

## Building TheBox Service Containers (Linux Containers)

```bash
# build Linux containers
make
```

or (Windows):

```dos
REM build Linux containers
make
```

## Developing/debugging the services in x86 containers locally (Linux Containers)

Please make sure to:

- use vscode and install (Remote Debugging Extension Pack)[https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack]
- create or update <project_root>/.vscode/launch.json with following Python debugging configurations:
  ```json
  {
    "version": "0.2.0",
    "configurations": [
      {
        "name": "Python: Module (thebox.inference)",
        "type": "python",
        "request": "launch",
        "module": "thebox.inference",
        "args": ["-c", "/config.yml"],
        "env": { "PYTHONPATH": "/workspace/thebox/services/src" },
        "console": "integratedTerminal"
      },
      {
        "name": "Python: Module (thebox.orchestrator)",
        "type": "python",
        "request": "launch",
        "module": "thebox.orchestrator",
        "args": ["-c", "/config.yml"],
        "env": { "PYTHONPATH": "/workspace/thebox/services/src" },
        "console": "integratedTerminal"
      },
      {
        "name": "Python: Module (thebox.notification)",
        "type": "python",
        "request": "launch",
        "module": "thebox.notification",
        "args": ["-c", "/config.yml"],
        "env": { "PYTHONPATH": "/workspace/thebox/services/src" },
        "console": "integratedTerminal"
      }
    ]
  }
  ```
- update (compose.extend.yml)[./compose.extend.yml] if a difference service container need to be debugged, by overriding the 'command' parameter to not start that service explicitly

Once above are done, do a:

```
make
```

to build the x86 containers, then click the green '><' icon to the bottome left of the vscode UI (or Ctrl+Shift+p and type in 'remote-containers: open folder in Container'), and open one of the following folder to debug the corresponding service:

- [thebox/docker/inference/inference](./inference/inference/)
- [thebox/docker/notification](./notification/)
- [thebox/docker/orchestrator](./orchestrator/)

VSCode will mount the source tree under /workspace folder inside the container and open up a terminal window. You can use Debug (Ctrl+Shift+D) panel to run one of the debug configurations specified earlier to start a particular service. Please use the matching service and container folder though (e.g. if your current VSCode opens the 'thebox/docker/inference/inference', then please use 'Python: Module (thebox.inference)' debug configuration).

## Running x86 containers locally (Linux Containers, without debugging)

Ramp up the containers:

```bash
docker-compose -f compose.yml up -d
```

Ramp down the conatiners:

```bash
docker-compose -f compose.yml down
```

## Building ARM containers for running on the real prototype hardware (RPIs+JetsonNano):

To build the containers for the target H/W architecture (ARM/ARM64):

```bash
# make you you have already build/rebuilt *.whl files first
# then build arm* containers
make prod
```

or (Windows):

```dos
REM make you you have already build/rebuilt *.whl files first
REM then build arm* containers
make prod
```

The first time build will take a long time. Especially the Jetson containers (can take up to several hours). Once it is cached, the build will be faster on code change iterations as the base Jetson containers will be cached properly.

To push the containers to the private registry:

```bash
# verify the dist files are built already, if not, build it first
docker images | grep thebox

# push to a private docker registry. e.g.
# remember to set DOCKER_REGISTRY, e.g. to theboxrouter.guest.corp.microsoft.com:2243
# if the registry is https and the CA trust cannot be done, you
# can modify /etc/docker/daemon.json to ignore the cert error
make push_prod
```

or (Windows):

```dos
REM verify the dist files are built already, if not, build it first
docker images | grep thebox

REM push to a private docker registry. e.g.
REM remember to set DOCKER_REGISTRY, e.g. to theboxrouter.guest.corp.microsoft.com:2243
REM if the registry is https and the CA trust cannot be done, you
REM can modify C:\ProgramData\Docker\config\daemon.json to ignore
REM the cert error
make push_prod
```

## Building TheBox Service Containers (Windows Containers)

```dos
REM build Windows containers
make windows
```

If you need to specify a specific Windows version (or running on a pre-release version of Windows), you should override WINVER flag in the env.private file. E.g.:

```
WINVER=1909
```

## Running x86 containers locally (Windows Containers, without debugging)

First, make you have switched to 'Windows Containers' if you are using Docker for Windows.

To ramp up the containers:

```dos
docker-compose -f compose.win.yml up -d
```

To ramp down the conatiners:

```dos
docker-compose -f compose.win.yml down
```
