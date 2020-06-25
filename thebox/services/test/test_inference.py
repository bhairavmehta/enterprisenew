import unittest
import numpy as np
import datetime
import time
import os
import shutil
from PIL import Image

from thebox.common.config import Config
from thebox.common.pubsub import PubSubManager
from thebox.common.scenario import InferenceDefinition
from thebox.common.model import ModelType, DataType, ModelDescriptor, ModelIODescriptor
from thebox.common.prediction import PredictionDataDescriptor, PredictionType
from thebox.pubsub_kafka.pubsubkafka import PubSubConnectionKafka, PubSubManagerKafka
from thebox.inference.inferenceservice import InferenceService
from thebox.inference.inferenceinstance import InferenceServiceInstance
from thebox.inference.modelcache import ModelCache
from thebox.messages.predictionmessage import PredictionMessage, ClassificationPredictionData
from thebox.messages.inferencemessage import InferenceMessage, InferenceDataFeature
from thebox.messages.orchestrationmessage import OrchestrationMessage

from .testbase import TestBase
from .testdb import setup_empty_test_db_server, initialize_test_db
from .testpubsub import setup_empty_test_pubsub_server


class TestInference(TestBase):

    @classmethod
    def setUpClass(self):
        self.test_pubsub_conn = setup_empty_test_pubsub_server()
        self.test_db_conn = setup_empty_test_db_server()

    def setupTestPubsubTopics(self) -> PubSubManager:

        self.test_orch_topic = "unittest_orchestration_topic"
        self.test_scn_in_topic = "unittest_scenario_in_topic"
        self.test_scn_out_topic = "unittest_scenario_out_topic"
        self.test_infer_store = "unittest_table_inference"
        self.test_service_client_name = "unittest_inference_service"

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
  inference-service-store-name: {self.test_infer_store}
  service-client-name: {self.test_service_client_name}
  model_cache_location: '/var/tmp/thebox_test'
"""
        self.cfg = Config(None, config)
        print(self.cfg)

        initialize_test_db(self.test_db_conn, self.test_infer_store)

        pubsubmgr = PubSubManagerKafka(self.test_pubsub_conn)
        pubsubmgr.reset()
        time.sleep(5)

        pubsubmgr.create_topic_if_not_exist(self.test_orch_topic)
        pubsubmgr.create_topic_if_not_exist(self.test_scn_in_topic)
        pubsubmgr.create_topic_if_not_exist(self.test_scn_out_topic)

        return pubsubmgr

    @staticmethod
    def read_image_as_numpy_array(filepath: str):
        # PIL read image already as RGB
        img = np.asarray(Image.open(filepath))
        return img

    def inference_test_model_variations(self):
        return {
            'simple': {
                'model_def': ModelDescriptor(
                    model_type=ModelType.ONNX,
                    model_name="test_onnx",
                    model_input_info=[
                        ModelIODescriptor(data_name="main_input", data_type=DataType.float32, data_shape=[1, 3])
                    ],
                    model_output_info=[
                        ModelIODescriptor(data_name="main_output/Sigmoid:0", data_type=DataType.float32, data_shape=[1, 1])
                    ],
                    model_location="test/testdata/test_model.onnx"
                ),
                'test_data': [
                    InferenceDataFeature(
                        "main_input", np.array([0,1,1]).astype(np.float32)
                    )
                ],
                'validation': lambda pred_data: \
                    len(pred_data) == 1 and \
                    pred_data['main_output/Sigmoid:0'].data[0] > 0.5 and pred_data['main_output/Sigmoid:0'].data[0] < 1.0
            },
            'multimodal': {
                'model_def': ModelDescriptor(
                    model_type=ModelType.ONNX,
                    model_name="test_onnx_multimodal",
                    model_input_info=[
                        ModelIODescriptor(data_name="app", data_type=DataType.float32, data_shape=[1, 141]),
                        ModelIODescriptor(data_name="url", data_type=DataType.float32, data_shape=[1, 5])
                    ],
                    model_output_info=[
                        ModelIODescriptor(data_name="dense_5/Sigmoid:0", data_type=DataType.float32, data_shape=[1, 1])
                    ],
                    model_location="test/testdata/test_multimodal_model.onnx.gz"
                ),
                'test_data': [
                    InferenceDataFeature(
                        "app", np.random.random([141]).astype(np.float32),
                    ),
                    InferenceDataFeature(
                        "url", np.random.random([5]).astype(np.float32),
                    )
                ],
                'validation': lambda pred_data: \
                    len(pred_data) == 1 and \
                    pred_data['dense_5/Sigmoid:0'].data[0] > 0.0 and \
                    pred_data['dense_5/Sigmoid:0'].data[0] < 1.0
            },
            'simpletf': {
                'model_def': ModelDescriptor(
                    model_type=ModelType.TENSORFLOW,
                    model_name="test_pb",
                    model_input_info=[
                        ModelIODescriptor(data_name="main_input", data_type=DataType.float32, data_shape=[1, 3])
                    ],
                    model_output_info=[
                        ModelIODescriptor(data_name="main_output/Sigmoid", data_type=DataType.float32, data_shape=[1, 1]),
                    ],
                    model_location="test/testdata/test_model.pb"
                ),
                'test_data': [
                    InferenceDataFeature(
                        "main_input", np.array([0,1,1]).astype(np.float32)
                    )
                ],
                'validation': lambda pred_data: \
                    len(pred_data) == 1 and \
                    pred_data['main_output/Sigmoid'].data[0] > 0.5 and pred_data['main_output/Sigmoid'].data[0] < 1.0
            }
        }


    def test_inferenceinstance(self):

        if os.path.exists("testdata_temp"):
            shutil.rmtree("testdata_temp")
        
        test_model_dict = self.inference_test_model_variations()

        for test_case in ['simple', 'simpletf']: #, 'multimodal']:
            model_def = test_model_dict[test_case]['model_def']
            infdef = InferenceDefinition(
                "test_in", 
                "test_out", 
                model_def, 
                PredictionDataDescriptor(PredictionType.CUSTOM)
                )
            model_cache = ModelCache("testdata_temp", self.log)
            infsvc = InferenceServiceInstance(infdef, model_cache, self.log)
            corr_id = f"{int(time.time())}"
            datapoint = InferenceMessage(corr_id, "unit test data", test_model_dict[test_case]['test_data'])

            pred = infsvc.run_inference(datapoint)
            self.assertEqual(corr_id, pred.correlation_id)
            print(f"prediction: {pred.prediction_data}")
            self.assertTrue(test_model_dict[test_case]['validation'](pred.prediction_data))


    def test_inferenceservice(self):
        
        if os.path.exists("testdata_temp"):
            shutil.rmtree("testdata_temp")
        
        test_model_dict = self.inference_test_model_variations()

        for test_case in ['simple']:
            pubsubmgr = self.setupTestPubsubTopics()

            infSvc = InferenceService(self.cfg)
            infSvc.start()

            # use a single correlation id for this test
            corr_id = f"{int(time.time())}"

            # post test scenario orchestration message to create a new scenario
            prod = pubsubmgr.create_producer(
                self.test_orch_topic, "unittest_test_producer")
            cons = pubsubmgr.create_consumer(
                [self.test_scn_out_topic], "unittest_test_consumer", "group1")
            time.sleep(2)

            # trigger creation of scenario
            inf_def = InferenceDefinition(
                self.test_scn_in_topic, 
                self.test_scn_out_topic, 
                test_model_dict[test_case]['model_def'], 
                PredictionDataDescriptor(PredictionType.CUSTOM)
                )
            prod.publish(OrchestrationMessage(corr_id, inf_def))
            time.sleep(5)

            # post some new test data point
            dataprod = pubsubmgr.create_producer(self.test_scn_in_topic, "unittest_test_producer")
            datapoint = InferenceMessage(corr_id, "unit test data", test_model_dict[test_case]['test_data'])
            dataprod.publish(datapoint)

            # wait for classification result to come out
            (topic_res, pred_res) = cons.poll(timeout=25)

            self.assertEqual(topic_res, self.test_scn_out_topic)
            self.assertTrue(len(infSvc.scenario_handlers) == 1)
            self.assertIsNotNone(pred_res)
            self.assertTrue(isinstance(pred_res, PredictionMessage))
            self.assertTrue(test_model_dict[test_case]['validation'](pred_res.prediction_data))

            infSvc.stop()


if __name__ == '__main__':
    unittest.main()
