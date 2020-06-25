from typing import List
from dataclasses import dataclass

from .ingestiondata import IngestionDataDescriptor
from .prediction import PredictionDataDescriptor
from .model import ModelDescriptor
from .notification import NotificationRule
from .repository import RootObject


@dataclass
class IngestionDefinition(object):
    in_topic: str = None
    out_topic: str = None
    data_descriptor: IngestionDataDescriptor = None


@dataclass
class InferenceDefinition(object):
    in_topic: str = None
    out_topic: str = None
    model_descriptor: ModelDescriptor = None
    pred_type: PredictionDataDescriptor = None


@dataclass
class NotificationDefinition(object):
    in_topic: str = None
    out_topic: str = None
    rules: List[NotificationRule] = None


@dataclass
class ScenarioDefinition(object):
    ingestion_definition: IngestionDefinition = None
    inference_definition: InferenceDefinition = None
    notification_definition: NotificationDefinition = None
