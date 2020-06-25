import json
from typing import List, Dict
import threading
import logging
from time import sleep, time

from thebox.common.config import Config
from thebox.common.scenario import NotificationDefinition, NotificationRule
from thebox.common.pubsub import PubSubManager, PubSubConsumer
from thebox.common_svc.base_service import BaseWorkerService
from thebox.common_svc.logging import acquire_service_logger
from thebox.pubsub_kafka.pubsubkafka import PubSubManagerKafka, PubSubConnectionKafka
from thebox.common.abstractmessage import AbstractMessage
from thebox.messages.predictionmessage import PredictionMessage
from thebox.messages.notificationmessage import NotificationMessage
from thebox.messages.orchestrationmessage import OrchestrationMessage
from thebox.db_couchdb.couchdb_repository_helper import CouchDbConnection
import thebox.common.defaults as default

from .notification_definition_repository import NotificationDefinitionRepository
from .notificationhandler import NotificationHandler
from .notification_object import Notification


class NotificationService(BaseWorkerService):
    """Notification service
       This service takes rule set and prediction results and translates them into
       notifications
    """
    # the channel that the orchestrator calls this service
    NOTIFICATION_SERVICE_STORE_NAME_DEFAULT = "table_notification_service"

    def __init__(self, config: Config):

        orchestration_topic = config.try_get(
            'servicesettings.orchestration-channel-in', default.ORCHESTRATION_NOTIF_TOPIC_DEFAULT)
        client_name = config.try_get(
            'servicesettings.service-client-name', None)
        self.__notification_service_store_name = config.try_get(
            'servicesettings.notification-service-store-name', NotificationService.NOTIFICATION_SERVICE_STORE_NAME_DEFAULT)

        # load configurations
        self.__db_conn = CouchDbConnection(
            config['store.couchdb.connection'],
            config['store.couchdb.username'],
            config['store.couchdb.usertoken']
        )
        self.__pubsub_conn = PubSubConnectionKafka(
            config['eventqueue.kafka.server']
        )

        # intialize db readers
        self.__noti_repo = NotificationDefinitionRepository(
            self.__db_conn, self.__notification_service_store_name)

        # initialize message bus manager
        self.__pubsub_mgr = PubSubManagerKafka(
            self.__pubsub_conn, acquire_service_logger())

        super().__init__(orchestration_topic, self.__pubsub_mgr, client_name)

        # initialize handlers
        self.__update_handlers()

        # logging the client name for debugging
        self.log.debug(
            f"Created instance with client name {self._BaseWorkerService__client_name}")

    def __update_handlers(self) -> Dict:
        noti_defs = self.__noti_repo.load_all()
        self.notification_handlers = {
            n.notification_definition.in_topic: NotificationHandler(
                n.notification_definition, self.log)
            for n in noti_defs
        }
        return [(n.notification_definition.in_topic, n.notification_definition.out_topic) for n in noti_defs]
    #
    # implement virtual method of the base class
    #

    def handle_orchestration_message(self, msg: AbstractMessage) -> bool:
        assert type(msg) is OrchestrationMessage
        assert type(msg.orchestration_data) is NotificationDefinition
        notif = Notification(notification_definition=msg.orchestration_data)
        self.__noti_repo.save(notif)
        return True

    def handle_scenario_message(self, topic: str, msg: AbstractMessage) -> List[AbstractMessage]:
        self.log.debug(
            f"Handling message with topic {topic}: {str(msg)[0:256]} ...")
        assert type(msg) is PredictionMessage

        if (topic in self.notification_handlers):
            notifs = self.notification_handlers[topic].handle_prediction(
                msg.prediction_data)
            if (notifs is not None and isinstance(notifs, List) and len(notifs) > 0):
                assert all(type(nid) is str for nid in notifs)
                corr_id = msg.correlation_id
                return [NotificationMessage(corr_id, n, f"{n} is triggered at {time()}") for n in notifs]
            else:
                # no notification need to be raised
                return None
        else:
            raise Exception(f"unrecognized topic w/o handler: {topic}")

    def update_scenario_topics(self) -> List:  # List[(str, str)]:
        return self.__update_handlers()
