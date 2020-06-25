import unittest
from .testbase import TestBase

import numpy as np
import datetime
import time

from thebox.common.config import Config
from thebox.common.pubsub import PubSubManager
from thebox.common.scenario import NotificationDefinition
from thebox.common.notification import NotificationRule
from thebox.pubsub_kafka.pubsubkafka import PubSubConnectionKafka, PubSubManagerKafka
from thebox.messages.predictionmessage import PredictionData, ClassificationPredictionData, PredictionMessage
from thebox.messages.notificationmessage import NotificationMessage
from thebox.messages.orchestrationmessage import OrchestrationMessage
from thebox.notification.notificationhandler import NotificationHandler
from thebox.notification.notificationservice import NotificationService

from .testbase import TestBase
from .testdb import setup_empty_test_db_server, initialize_test_db
from .testpubsub import setup_empty_test_pubsub_server


class TestNotification(TestBase):

    @classmethod
    def setUpClass(self):
        self.test_pubsub_conn = setup_empty_test_pubsub_server()
        self.test_db_conn = setup_empty_test_db_server()

    def setupTestPubsubTopics(self) -> PubSubManager:

        self.test_orch_topic = "unittest_orchestration_topic"
        self.test_scn_in_topic = "unittest_scenario_in_topic"
        self.test_scn_out_topic = "unittest_scenario_out_topic"
        self.test_notif_store = "unittest_table_notification"
        self.test_service_client_name = "unittest_notification_service"

        config = f"""
# config.yml

version: 1.0
store:
  couchdb:
    connection: "{self.test_db_conn.url}"
    username: {self.test_db_conn.user}
    usertoken: {self.test_db_conn.token}
eventqueue:
  kafka:
    server: "{self.test_pubsub_conn.server_url}"
servicesettings:
  orchestration-channel-in: {self.test_orch_topic}
  notification-service-store-name: {self.test_notif_store}
  service-client-name: {self.test_service_client_name}
"""
        self.cfg = Config(None, config)

        initialize_test_db(self.test_db_conn, self.test_notif_store)

        pubsubmgr = PubSubManagerKafka(self.test_pubsub_conn)
        pubsubmgr.reset()
        time.sleep(5)

        pubsubmgr.create_topic_if_not_exist(self.test_orch_topic)
        pubsubmgr.create_topic_if_not_exist(self.test_scn_in_topic)
        pubsubmgr.create_topic_if_not_exist(self.test_scn_out_topic)

        return pubsubmgr

    def test_notificationhandler(self):

        test_preds = [
            ClassificationPredictionData("person", 0.8, None),
            ClassificationPredictionData("car", 0.2, None),
        ]

        # positive test case
        notif_def = NotificationDefinition(
            "test_inf_topic_out",
            "test_scn_notify_topic",
            [
                NotificationRule(
                    "person_detected", "any(p.class_label == 'person' for p in prediction)", "test_notification")
            ]
        )
        handler = NotificationHandler(notif_def, self.log)
        notifs = handler.handle_prediction(test_preds)
        assert "test_notification" in notifs

        # negative test case
        notif_neg_def = NotificationDefinition(
            "test_inf_topic_out",
            "test_scn_notify_topic",
            [
                NotificationRule(
                    "person_detected", "any(p.class_label == 'car' and p.probability > 0.5 for p in prediction)", "test_notification")
            ]
        )
        handler = NotificationHandler(notif_neg_def, self.log)
        notifs = handler.handle_prediction(test_preds)
        assert notifs is None

    def test_notificationservice(self):

        pubsubmgr = self.setupTestPubsubTopics()

        # self, orch_topic=None, config: Config = None, client_name=None, svc_store_name=None
        notifSvc = NotificationService(self.cfg)
        notifSvc.start()

        # use a single correlation id for this test
        corr_id = f"{int(time.time())}"

        # post test scenario orchestration message to create a new scenario
        prod = pubsubmgr.create_producer(
            self.test_orch_topic, "unittest_test_producer")
        cons = pubsubmgr.create_consumer(
            [self.test_scn_out_topic], "unittest_test_consumer", "group1")
        time.sleep(2)
        notif_def = NotificationDefinition(
            self.test_scn_in_topic,
            self.test_scn_out_topic,
            [
                NotificationRule(
                    "person_detected", "any(p.class_label == 'person' for p in prediction)", "test_notification")
            ]
        )
        prod.publish(OrchestrationMessage(corr_id, notif_def))
        time.sleep(5)

        # post some inference result (prediction) data
        dataprod = pubsubmgr.create_producer(
            self.test_scn_in_topic, "unittest_test_producer")
        datapoint = PredictionMessage(corr_id, [
            ClassificationPredictionData("person", 0.8, None),
            ClassificationPredictionData("car", 0.2, None),
        ])
        dataprod.publish(datapoint)
        time.sleep(5)

        # make sure that notification message was generated
        res = []
        while True:
            (topic_res, notif_res) = cons.poll(timeout=5)
            if (topic_res is None):
                break  # no more messages
            res.append((topic_res, notif_res))

        self.assertTrue(all(r[0] == self.test_scn_out_topic for r in res))
        self.assertTrue(
            all(isinstance(r[1], NotificationMessage) for r in res))
        self.assertTrue(len(res) == 1)
        self.assertTrue(all(r[1].notification_id ==
                            "test_notification" for r in res))

        notifSvc.stop()


if __name__ == '__main__':
    unittest.main()
