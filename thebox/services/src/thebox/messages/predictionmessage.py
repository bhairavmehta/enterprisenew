from typing import List, Dict, TypeVar
from dataclasses import dataclass

from thebox.common.abstractmessage import AbstractMessage


@dataclass
class PredictionData(object):
    """Base type of prediction result
    """

    def __str__(self) -> str:
        return self.__repr__()


@dataclass
class ClassificationPredictionData(PredictionData):
    class_label: str
    probability: float
    data: Dict[str, object] = None

    def __post_init__(self):
        self.prediction_type = "Classification"


@dataclass
class CustomPredictionData(PredictionData):
    data: object

    def __post_init__(self):
        self.prediction_type = "Custom"


@dataclass
class PredictionMessage(AbstractMessage):
    # a diction of predictions made by the inference service
    # with prediction's name
    prediction_data: Dict[str, PredictionData]
