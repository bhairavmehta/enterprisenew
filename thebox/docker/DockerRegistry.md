# How to create a private Docker registry

## Creating a registry using docker-compose

Best way to create a registry is to use docker itself.

Below is a docker-compose example of creating a private insecure HTTP registry on port 5000 plus a simple registry explorer web ui on port 5001 on a x86 host:

```yml
version: "2.0"
services:
  registryv2:
    image: registry:latest
    restart: always
    ports:
      - 5000:5000
    volumes:
      - ${LOCAL_REGISTRY_STORE_PATH}:/var/lib/registry
    environment:
      - REGISTRY_HTTP_ADDR=0.0.0.0:5000
      - REGISTRY_STORAGE_DELETE_ENABLED=true
    networks:
      - registry-ui-net

  ui:
    image: joxit/docker-registry-ui:static
    restart: always
    ports:
      - 5001:80
    environment:
      - REGISTRY_TITLE=My Private Registry
      - REGISTRY_URL=http://registryv2:5000
      - DELETE_IMAGES=true
    depends_on:
      - registryv2
    networks:
      - registry-ui-net

networks:
  registry-ui-net:
```

Typically, I would recommend using the PI which hosts the K8s master node of TheBox for hosting the registry, as it is not used for running the services.

You can also put the registry on an external x86 server, but you have to make sure that the K8s cluster can resolve the FQDN of the server.


## Creating a self-signed SSL cert for a secure registry

Optionally, if you want to enable HTTPS for the registry, you will need to:

* Create a private CA (certificate authority) key and CA root certificate
* Create a private key for the registry server, sign it with CA root certificate and generated the registry server's certificate
* Deploy the root CA certificate to all nodes in TheBox
* Make the registry server's key and certificate available to the docker registry container

### Detailed explanation

You can follow [this guide](https://forum.hilscher.com/Thread-Setup-trusted-Docker-registry-on-a-Raspberry-Pi-to-host-netPI-containers). 

Tips how to use the guide:
* Step 1-10 shows how to prepare to generate the cert. You do not need to follow literally if you already done it or have a different setup (E.g. hostname, installing docker etc.)
* Step 11 to 16 shows how to generate the CA private key, CA root certificate, as well as registry server's private key and certificate cross-signed by the CA root certificate. You will need to customize the parameter you passed in (e.g. file names, and metadata specified in CSR (Certificate Sign Request))
* Step 17 shows how to deploy the CA root certificate to a node (PI or Jetson device)
    * Step 18 shows how to share the certificate with the docker registry. You will need to customize the docker-compose yml file to add a few parameters to pointing to the certificate files, here is an example:

    ```yml
    version: '2.0'
    services:
    registryv2:
        image: registry:latest
        ports:
        - 443:443
        volumes:
        - /home/pi/registry-data:/var/lib/registry
        - /home/pi/certs:/certs
        environment:
        - REGISTRY_HTTP_ADDR=0.0.0.0:443
        - REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt
        - REGISTRY_HTTP_TLS_KEY=/certs/domain.key
        - REGISTRY_STORAGE_DELETE_ENABLED=true
        restart: always
        networks:
        - registry-ui-net

    ui:
        image: joxit/docker-registry-ui:arm32v7-static
        ports:
        - 80:80
        environment:
        - REGISTRY_TITLE=TheBox's Private Registry
        - REGISTRY_URL=https://registryv2:443
        - DELETE_IMAGES=true
        depends_on:
        - registryv2
        restart: always
        networks:
        - registry-ui-net

    networks:
    registry-ui-net:

    ```
    Above assumes the private key and certificate are placed in /home/pi/certs folder.
