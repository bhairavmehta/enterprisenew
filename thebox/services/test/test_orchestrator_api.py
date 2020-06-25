
# Example test scenario JSON:
"""
{
  "scenario_name": "test scenario",
  "scenario_definition":
  {
    "inference_definition":
    {
      "in_topic": "in_topic_infer_test",
      "out_topic": "out_topic_infer_test",
      "model_descriptor":
      {
        "model_type": "PREBUILT",
        "model_name": "ResNet50_v2"
      },
      "pred_type":
      {
        "prediction_data_type": "classificationtype"
      }
    },
    "notification_definition":
    {
      "in_topic": "out_topic_infer_test",
      "out_topic": "out_topic_notif_test",
      "rules": [
        {
          "rule_name": "person_detected", 
          "rule_content": "any('cat' in p.class_label for p in prediction)", 
          "notification_id": "test_notification"
        }
      ]
    }
  }
}
"""
