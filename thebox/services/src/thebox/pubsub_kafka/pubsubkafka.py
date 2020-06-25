from typing import List
from confluent_kafka.admin import AdminClient, NewTopic
from confluent_kafka import Producer, Consumer, KafkaError
import pprint
import datetime
import jsonpickle
import json
import logging

from thebox.common.abstractmessage import AbstractMessage
from thebox.common.connection import Connection
from thebox.common.pubsub import PubSubManager, PubSubConsumer, PubSubProducer


class PubSubConnectionKafka(Connection):
    def __init__(self, server_url: str):
        self.server_url = server_url
        super(PubSubConnectionKafka, self).__init__("kafka")


class PubSubProducerKafka(PubSubProducer):
    def __init__(self, conf: dict, topic_name: str, client_name: str, logger: logging.Logger = None):
        self.topic_name = topic_name
        self.client_name = client_name
        self.__producer = Producer(conf)
        self.__log = logger

    def __log(self, msg: str):
        if (self.__logger is not None):
            self.__logger.debug(msg)

    def publish(self, msg: AbstractMessage):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msgjson = jsonstr = jsonpickle.encode(msg)
        self.__producer.produce(
            self.topic_name, key=timestamp, value=msgjson)  # returns Future
        self.__producer.flush()  # sync


class PubSubConsumerKafka(PubSubConsumer):
    def __init__(self, conf: dict, topic_names: List[str], client_name: str, group_name: str, logger: logging.Logger = None):
        self.client_name = client_name
        self.__consumer_settings = {
            'bootstrap.servers': conf['bootstrap.servers'],
            'group.id': group_name,
            'client.id': client_name,
            'enable.auto.commit': True,
            'session.timeout.ms': 6000,
            'default.topic.config': {'auto.offset.reset': 'smallest'}
        }
        self.__consumer = None
        self.__set_consumer(topic_names)
        self.__log = logger

    def __set_consumer(self, topic_names: List[str]):
        if (len(topic_names) > 0):
            if (self.__consumer is None):
                self.__consumer = Consumer(self.__consumer_settings)
            #print(f"DEBUG: __set_consumer: {topic_names}")
            self.__consumer.subscribe(topic_names)
        else:
            if (self.__consumer is not None):
                self.__consumer.unsubscribe()

    def __log(self, msg: str):
        if (self.__logger is not None):
            self.__logger.debug(msg)

    def reset_topics(self, topic_names: List[str]):
        self.__set_consumer(topic_names)

    # returns a pair (topic, msg)
    def poll(self, timeout=None) -> (str, object):
        if (timeout is None):
            timeout = 1

        if (self.__consumer is None):
            return (None, None)

        msg = self.__consumer.poll(timeout)
        if (msg is None):
            return (None, None)
        elif not msg.error():
            #print(f"DEBUG: PubSubConsumerKafka: Message Received: {msg.value()[0:256]} ...")
            return (msg.topic(), jsonpickle.decode(msg.value()))
        elif msg.error().code() == KafkaError._PARTITION_EOF:
            self.__log(
                f"End of partition reached {msg.topic()}/{msg.partition()}")
            return (None, None)
        else:
            self.__log(f"Error occured: {msg.error().str()}")
            return (None, None)


class PubSubManagerKafka(PubSubManager):
    def __init__(self, conn: Connection, logger: logging.Logger = None):
        # References to the configuration for librdkafka:
        # https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
        self.__pubsub_conf = {
            'bootstrap.servers': conn.server_url,
            'message.max.bytes': 10485760 # 10M default size
            }
        self.__logger = logger

    def create_topic_if_not_exist(self, topic_name: str):
        kafka_admin = AdminClient(self.__pubsub_conf)
        if (topic_name not in kafka_admin.list_topics().topics):
            new_topic = NewTopic(topic_name, 1, 1)
            new_topic_creation = kafka_admin.create_topics([new_topic, ])
            for topic, f in new_topic_creation.items():
                try:
                    f.result()  # The result itself is None
                    self.__log(f"Topic {topic} created")
                except Exception as e:
                    self.__log(f"Failed to create topic {topic}: {e}")

    def __log(self, msg: str):
        if (self.__logger is not None):
            self.__logger.debug(msg)

    def test_connection(self):
        try:
            kafka_admin = AdminClient(self.__pubsub_conf)
            topics = kafka_admin.list_topics(timeout=1).topics
            return True
        except Exception as e:
            return False

    # delete all topics and data came with it
    def reset(self):
        kafka_admin = AdminClient(self.__pubsub_conf)
        topics = kafka_admin.list_topics().topics
        if (len(topics) > 0):
            topic_deletes = kafka_admin.delete_topics(list(topics.keys()))
            for topic, f in topic_deletes.items():
                try:
                    f.result()  # The result itself is None
                    self.__log(f"Topic {topic} deleted")
                except Exception as e:
                    self.__log(f"Failed to delete topic {topic}: {e}")

    def create_producer(self, topic_name: str, client_name: str) -> PubSubProducer:
        return PubSubProducerKafka(self.__pubsub_conf, topic_name, client_name, self.__logger)

    def create_consumer(self, topic_names: List[str], client_name: str, group_name: str) -> PubSubConsumer:
        return PubSubConsumerKafka(self.__pubsub_conf, topic_names, client_name, group_name, self.__logger)
