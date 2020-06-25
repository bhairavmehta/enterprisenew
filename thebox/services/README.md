# The Box - Services

This folder contains the code runs inside 'The Box'.

The services are microservices that are fulfilling multiple roles:

- Orchestrator: configuration interface to The Box and provisions scenarios to run on the worker micro services
- Ingestion Service: take raw data format from external providesr and adapt them into what's required by Inference Service
- Inference Service: using CPU/GPU to run ML inference workload
- Notification Service: act on inference result and produce notifications to be subscribed by external apps

![The Box Architecture](docs/thebox_v2.png)

## Preparations

1. Install Docker and Docker Compose

   ```bash
   # install docker and docker compose
   curl -sSL https://get.docker.com | sh
   sudo usermod pi -aG docker
   newgrp docker
   sudo apt-get update && apt-get install docker-compose
   ```

   or (Windows):

   ```batch
   REM under elevated command line
   choco install docker-desktop
   ```

2. Install Python3, virtual env and create a new dev environment:

   ```bash
   sudo apt-get install virtualenv python3 python3-pip
   sudo -H pip3 install virtualenvwrapper
   mkdir ~/github_projects
   echo "# Python Virtualenv Settings" >> ~/.bashrc
   echo export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3.6 >> ~/.bashrc
   echo export WORKON_HOME=\$HOME/.virtualenvs >> ~/.bashrc
   echo export PROJECT_HOME=\$HOME/github_projects >> ~/.bashrc
   echo source /usr/local/bin/virtualenvwrapper.sh >> ~/.bashrc
   source ~/.bashrc
   mkvirtualenv thebox_dev -p ${VIRTUALENVWRAPPER_PYTHON}
   workon thebox_dev
   ```

   or (Windows):

   ```batch
   REM under elevated command line
   choco install anaconda3

   REM Open the Anaconda cmd prompt
   %CONDA_EXE% create -n thebox_dev python=3.6
   cmd /k "%CONDA_PREFIX%\Scripts\activate.bat %CONDA_PREFIX%\envs\thebox_dev & title Conda thebox_dev"
   ```

3. Install required packages by:

   ```bash
   pip install -r requirements.txt
   ```

4. In order to cross build ARM, run following command to register the QEMU handlers:

   ```bash
   # see https://github.com/multiarch/qemu-user-static
   docker run --rm --privileged multiarch/qemu-user-static:register
   # to confirm if registration exists
   ls -l /proc/sys/fs/binfmt_misc
   ```

5. If there is a workaround.py in the enlistment, run it once too after step 4.:

   ```bash
   python workaround.py
   ```

6. If you want to manually call Orchestartor API, it is recommended that you get a Swagger instance running.
   For example, run a swagger locally on port 1080:
   ```bash
   docker run -d -p 1080:8080 swaggerapi/swagger-ui:v2.2.9
   ```

## Run Tests

The project uses Python unittest framework and requires dev box to be able to run docker as the current user.

To run all unit tests, type:

```bash
./runtest.sh
```

or (Windows):

```batch
.\runtest.cmd
```

## Develop and run The Box services in the container environment

This is the recommended way to debug service code, as the code will run in the similar environment as when it is deployed later. To do this, please follow the section 'Developing/debugging the services in x86 containers' in [this](../docker/README.md) guide.

## Develop and run The Box services outside of the container environment

First, run unittest at least once, which will create the test containers (Kafka and CouchDB).
Then run these commands in different terminal to start difference services piece:

```bash
# orchestrator service
./start_svc.sh orch

# inference service
./start_svc.sh infer

# notification service
./start_svc.sh notif
```

or (Windows):

```batch
REM orchestrator service
.\start_svc.cmd orch

REM inference service
.\start_svc.cmd infer

REM notification service
.\start_svc.cmd notif
```

## Build Distribution Packages for containernization

Requires Python3, as well Python3 packages setuptools and wheels to be installed:

To build, type:

```bash
./build_dist.sh
```

or (Windows):

```batch
.\build_dist.cmd
```

## Build containers, run it locally and publish to The Box hardware

Please refers to this [link](../dockers/README.md).

## TODOs

- bug: potential racing condition on worker service starts before orch service
- K8s template: need persisting volumes for couchdb and kafka
- bug: k8s template: no hard dependency can be set, currently if kafka starts before zookeeper it can crash. need to add retry wait
- code orchestrator service
  - finish on the rest api
  - create / delete scenarios + publish topics to worker services + create kakfa topics
  - BUG: get crashes the orch api
- migration from flask-restful (seems out of support) to https://github.com/noirbizarre/flask-restplus
- deployment using dockerfiles + dockercompose
  - fix a design issue where the api starts before db is ready

## Hacks (To be removed in future)

1. Bug in flask_restful_swagger.
   Solution: Please run workaround.py after pulled the requirements.

## References

- Object-Mapper: https://github.com/marazt/object-mapper
- Flask-Restful: https://flask-restful.readthedocs.io/en/latest/api.html#flask_restful.Api.add_resource
- Flask-Marshmallow: https://github.com/marshmallow-code/flask-marshmallow
- Marshmallow: https://marshmallow.readthedocs.io/en/3.0/quickstart.html#serializing-objects-dumping
