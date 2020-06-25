import json
from typing import List
import threading
from time import sleep

from thebox.common.config import Config
from thebox.common.scenario import InferenceDefinition
from thebox.common.pubsub import PubSubManager, PubSubConsumer
from thebox.common_svc.base_service import BaseWorkerService
from thebox.common_svc.logging import acquire_service_logger
from thebox.pubsub_kafka.pubsubkafka import PubSubManagerKafka, PubSubConnectionKafka
from thebox.common.abstractmessage import AbstractMessage
from thebox.messages.inferencemessage import InferenceMessage
from thebox.messages.predictionmessage import PredictionMessage
from thebox.messages.orchestrationmessage import OrchestrationMessage
from thebox.db_couchdb.couchdb_repository_helper import CouchDbConnection
import thebox.common.defaults as default

from .inference_definition_repository import InferenceDefinitionRepository
from .inferenceinstance import InferenceServiceInstance
from .inference_object import Inference
from .modelcache import ModelCache


class InferenceService(BaseWorkerService):

    # the channel that the orchestrator calls this service
    INFERENCE_SERVICE_STORE_NAME_DEFAULT = "table_inference_service"

    def __init__(self, config: Config):

        orchestration_topic = config.try_get(
            'servicesettings.orchestration-channel-in', 
            default.ORCHESTRATION_INFER_TOPIC_DEFAULT
            )
        client_name = config.try_get(
            'servicesettings.service-client-name', 
            None
            )
        self.__inference_service_store_name = config.try_get(
            'servicesettings.inference-service-store-name', 
            InferenceService.INFERENCE_SERVICE_STORE_NAME_DEFAULT
            )

        # load configurations
        self.__db_conn = CouchDbConnection(
            config['store.couchdb.connection'],
            config['store.couchdb.username'],
            config['store.couchdb.usertoken']
        )
        self.__pubsub_conn = PubSubConnectionKafka(
            config['eventqueue.kafka.server']
        )
        self.__model_cache_location = config.try_get(
            'servicesettings.model_cache_location', 
            default.MODEL_CACHE_LOCATION
            )

        # intialize db readers
        self.__infer_repo = InferenceDefinitionRepository(
            self.__db_conn, self.__inference_service_store_name)

        # initialize message bus manager
        self.__pubsub_mgr = PubSubManagerKafka(
            self.__pubsub_conn, acquire_service_logger())

        super().__init__(orchestration_topic, self.__pubsub_mgr, client_name)

        # initialize model cache
        self.__model_cache = ModelCache(self.__model_cache_location, self.log)

        # logging the client name for debugging
        self.log.debug(
            f"Created instance with client name {self._BaseWorkerService__client_name}")

    #
    # implement virtual method of the base class
    #

    def handle_orchestration_message(self, msg: AbstractMessage) -> bool:
        assert type(msg) is OrchestrationMessage
        assert type(msg.orchestration_data) is InferenceDefinition
        inf = Inference(inference_definition=msg.orchestration_data)
        self.__infer_repo.save(inf)
        return True

    def handle_scenario_message(self, topic: str, msg: AbstractMessage) -> List[AbstractMessage]:
        self.log.debug(
            f"Handling message with topic {topic}: {str(msg)[0:256]})")
        assert type(msg) is InferenceMessage
        # TODO:
        # maintain a message queue / worker thread pool, instead of in-proc
        # prediction
        if (topic in self.scenario_handlers):
            pred = self.scenario_handlers[topic].run_inference(msg)
            assert type(pred) is PredictionMessage
            return [pred]
        else:
            raise Exception(f"unrecognized topic w/o handler: {topic}")

    def update_scenario_topics(self) -> List:  # List[(str, str)]:
        inf_defs = self.__infer_repo.load_all()
        self.scenario_handlers = {
            inf.inference_definition.in_topic:
            InferenceServiceInstance(inf.inference_definition, self.__model_cache, self.log) for inf in inf_defs
        }
        return [(inf.inference_definition.in_topic, inf.inference_definition.out_topic) for inf in inf_defs]
