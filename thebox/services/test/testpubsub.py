import docker
import time
import yaml
from io import StringIO
from .dockercompose import *

from thebox.common.connection import Connection
from thebox.pubsub_kafka.pubsubkafka import PubSubConnectionKafka, PubSubManagerKafka


kafka_test_docker_compose_content = """
version: '2'
services:
  zookeeper:
    image: wurstmeister/zookeeper
    ports:
      - "2181:2181"
  kafka:
    image: wurstmeister/kafka
    ports:
      - "9092:9092"
    depends_on:
      - zookeeper
    environment:
      KAFKA_ADVERTISED_HOST_NAME: localhost
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
"""

kafka_test_config_content = """
kafka_container_port: 9092
kafka_host_name: localhost
"""


def setup_empty_test_pubsub_server() -> PubSubConnectionKafka:
    client = docker.from_env()

    # setup zookeeper/kafka
    kafka_test_config = yaml.load(
        StringIO(kafka_test_config_content), Loader=yaml.SafeLoader)

    test_project_name = "unittest"

    conn_obj = PubSubConnectionKafka(
        f"{kafka_test_config['kafka_host_name']}:{kafka_test_config['kafka_container_port']}"
    )

    if f"{test_project_name}_kafka_1" not in [c.name for c in client.containers.list()]:
        setup_test_containers_with_docker_compose(
            kafka_test_docker_compose_content, test_project_name)

        # test the connection to wait for container launch
        pubsub = PubSubManagerKafka(conn_obj)
        if not pubsub.test_connection():
            print("Waiting for kafka container to start ...")
            time.sleep(5)
            while not pubsub.test_connection():
                print("Still waiting ...")
                time.sleep(5)
        print(
            f"Test containers '{test_project_name}_kafka_1': has been started")

        # hack: leave sometime for kafka to warm up
        print("Pausing a bit for kafka to warm up ...")
        time.sleep(30)
    else:
        print(
            f"skip creating test containers '{test_project_name}_kafka_1': already exist")

    return conn_obj
