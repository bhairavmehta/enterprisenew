# The Box Demo Using Face Detection Models

## Preparation:

- Download an example DNN model
    ```
    wget -O facessd.pb https://github.com/yeephycho/tensorflow-face-detection/blob/master/model/frozen_inference_graph_face.pb?raw=true
    ```
- Deploy the model to a file server that is accessile by the box instance
  To start a simple file server with docker:
    ```
    # Make a server that will be available at http://localhost:8082:
    docker run -dit \
        --restart unless-stopped \
        -p 8082:80 \
        -v "<local_download_folder>":/usr/local/apache2/htdocs/ \
        --name model_file_server \
        httpd:2.4
    ```
- Create a scenario definition to consume the model by pointing to the upload location
- Run SigGen and Notif app


## References
- Tensorflow face detection using MobileNet SSD CNN: https://github.com/yeephycho/tensorflow-face-detection