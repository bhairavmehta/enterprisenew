from typing import List
from thebox.common.abstractmessage import AbstractMessage


# Abstract Producer
class PubSubProducer(object):
    def __init__(self, conf: dict, topic_name: str):
        self.topic_name = topic_name

    def publish(self, msg: AbstractMessage):
        raise NotImplementedError()


# Abstract Consumer
class PubSubConsumer(object):
    def __init__(self, conf: dict, topic_names: List[str]):
        self.client_name = client_name
        self.topic_names = topic_names

    # update the list of topics this pub sub consumer listens to
    def reset_topics(self, topic_names: List[str]):
        raise NotImplementedError()

    # poll messages
    # returns (topic, message object)
    def poll(self, timeout=None) -> (str, object):
        raise NotImplementedError()


# Abstract PubSub manager
class PubSubManager(object):

    # create a new topic
    def create_topic_if_not_exist(self, topic_name: str):
        raise NotImplementedError()

    # delete all topics and data came with it
    def reset(self):
        raise NotImplementedError()

    # create a new instance of producer
    def create_producer(self, topic_name: str, client_name: str) -> PubSubProducer:
        raise NotImplementedError()

    # create a new instance of consumer
    def create_consumer(self, topic_names: List[str], client_name: str, group_name: str) -> PubSubConsumer:
        raise NotImplementedError()
