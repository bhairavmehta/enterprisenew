import unittest

from thebox.common.ingestiondata import *
from thebox.common.model import *
from thebox.common.notification import *
from thebox.common.scenario import *
from thebox.common.prediction import *
from thebox.orchestrator.scenario_repository import *

from .testbase import TestBase
from .testdb import *


class TestScenario(TestBase):

    @classmethod
    def setUpClass(self):
        self.test_db_conn = setup_empty_test_db_server()

    def test_basic(self):
        initialize_test_db(self.test_db_conn, "unit_test_scenario")
        scn_repos = ScenarioRepository(self.test_db_conn, "unit_test_scenario")

        scenario = Scenario(
            None,
            "test scenario",
            ScenarioDefinition(
                IngestionDefinition(
                    "test_scn_topic_in",
                    "test_scn_topic_out",
                    IngestionDataDescriptor(
                        "camera feed",
                        [
                            FeatureDescriptor(
                                "feature_1", FeatureType.STRING, "this is a test")
                        ]),
                ),
                InferenceDefinition(
                    "test_scn_topic_out",
                    "test_inf_topic_out",
                    ModelDescriptor(ModelType.ONNX, "yolov3"),
                    PredictionDataDescriptor(PredictionType.CUSTOM)
                ),
                NotificationDefinition(
                    "test_inf_topic_out",
                    "test_scn_notify_topic",
                    [
                        NotificationRule(
                            "person_detected", "any(p.class_label == 'person' for p in prediction)", "test_notification")
                    ]
                )
            )
        )

        scenario_id = scn_repos.save(scenario)
        loaded_scenario = scn_repos.load(scenario_id)
        self.assertIsNotNone(loaded_scenario)
        self.assertEqual(loaded_scenario._id, scenario_id)

        loaded_scenario_2 = scn_repos.load_by_name("test scenario")
        self.assertIsNotNone(loaded_scenario_2)
        self.assertEqual(len(loaded_scenario_2), 1)
        self.assertEqual(loaded_scenario_2[0]._id, scenario_id)


if __name__ == '__main__':
    unittest.main()
