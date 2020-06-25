from typing import List
import json
import pickle as pkl
import threading
from time import sleep

from thebox.common.config import Config
from thebox.common.scenario import ScenarioDefinition, InferenceDefinition, NotificationDefinition
from thebox.common.pubsub import PubSubManager, PubSubConsumer
from thebox.common_svc.base_service import BaseService
from thebox.common_svc.service_error import ServiceParameterError
from thebox.common_svc.logging import acquire_service_logger
from thebox.common.abstractmessage import AbstractMessage
from thebox.messages.orchestrationmessage import OrchestrationMessage
from thebox.db_couchdb.couchdb_repository_helper import CouchDbConnection
from thebox.pubsub_kafka.pubsubkafka import PubSubConnectionKafka, PubSubManagerKafka
import thebox.common.defaults as default

from .scenario import Scenario
from .scenario_repository import ScenarioRepository


class OrchestrationService(BaseService):
    """This is the master service that is responsible for
       - take administrative input from external environment via API exposed
       - manages the communication channels (pubsub + message pipeline)
       - using orchestration message to direct other micro-services
    """

    ORCHESTRATION_SERVICE_STORE_NAME_DEFAULT = "table_orchestration_service"

    def __init__(self, config: Config):

        orch_infer_topic = config.try_get(
            'servicesettings.orchestration-inference-channel-in', default.ORCHESTRATION_INFER_TOPIC_DEFAULT)
        orch_notif_topic = config.try_get(
            'servicesettings.orchestration-notification-channel-in', default.ORCHESTRATION_NOTIF_TOPIC_DEFAULT)
        self.__scenario_store_name = config.try_get(
            'servicesettings.orchestration-service-store-name', OrchestrationService.ORCHESTRATION_SERVICE_STORE_NAME_DEFAULT)
        self.__client_name = config.try_get(
            'servicesettings.service-client-name', None)

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
        self.__scn_repo = ScenarioRepository(
            self.__db_conn, self.__scenario_store_name)

        # initialize message bus manager and producers
        self.__pubsub_mgr = PubSubManagerKafka(
            self.__pubsub_conn, acquire_service_logger())
        self.__pubsub_mgr.create_topic_if_not_exist(orch_infer_topic)
        self.__pubsub_mgr.create_topic_if_not_exist(orch_notif_topic)
        self.__producers = {
            'infer': self.__pubsub_mgr.create_producer(orch_infer_topic, self.__client_name),
            'notif': self.__pubsub_mgr.create_producer(orch_notif_topic, self.__client_name),
        }

        super().__init__()

    def __validate_scenario(self, scenario: Scenario):
        """
        Validate scenario input and raise exception with a 
        list of validation errors, if any
        """
        errors = []
        if (scenario.scenario_definition is None or
                type(scenario.scenario_definition) is not ScenarioDefinition):
            errors.append(("scenario.scenario_definition", "is not valid"))
        else:
            scn_def = scenario.scenario_definition

            if (scn_def.inference_definition is None or
                    type(scn_def.inference_definition) is not InferenceDefinition):
                errors.append(
                    ("scenario.scenario_definition.inference_definition", "is not valid"))

            if (scn_def.notification_definition is None or
                    type(scn_def.notification_definition) is not NotificationDefinition):
                errors.append(
                    ("scenario.scenario_definition.notification_definition", "is not valid"))

            # check topic coherence
            if (scn_def.notification_definition.in_topic !=
                    scn_def.inference_definition.out_topic):
                errors.append(
                    ("scenario.scenario_definition.notification_definition.in_topic",
                     "does not equal to inference_definition.out_topic")
                )

            # TODO:
            # validate the additional fields in inference/notification definition
            # decide on how to valid inference/notification_definition. should it done by
            # orchestration service or by individual worker service and post back the result

        if len(errors) > 0:
            raise ServiceParameterError(errors)

    # Public APIs

    def create_scenario(self, scenario: Scenario):
        self.__validate_scenario(scenario)

        scn_def = scenario.scenario_definition

        # create topics required by this scenario
        self.log.debug(
            f"Creating scenario pubsub topics ...")
        scn_topics = [
            scn_def.inference_definition.in_topic,
            scn_def.inference_definition.out_topic,
            scn_def.notification_definition.out_topic
        ]
        for t in scn_topics:
            self.__pubsub_mgr.create_topic_if_not_exist(t)

        # post messages and verify that they are sucessfully created
        corr_id = AbstractMessage.create_new_correlation_id()
        self.log.debug(
            f"Notify worker services for scenario creation: {scenario} "
            f"with corr-id = {corr_id} ..."
        )
        self.__producers['infer'].publish(
            OrchestrationMessage(corr_id, scn_def.inference_definition))
        self.__producers['notif'].publish(OrchestrationMessage(
            corr_id, scn_def.notification_definition))
        # TODO:
        # Wait for successful confirmation by the post back channel for creation message

        # save the scenario
        self.log.debug(f"Writing scenario: {scenario} ...")
        self.__scn_repo.save(scenario)

        # return creation result
        self.log.debug(f"Scenario succesfully created!")
        return scenario

    def get_scenarios(self) -> List[Scenario]:
        return self.__scn_repo.load_all()

    def delete_scenarios(self, scenario_id: str):
        # TODO:
        # validate if scenario exists
        # post messages to worker services to delete their respective definitions
        # delete the scenario
        raise NotImplementedError("delete_scenario")
