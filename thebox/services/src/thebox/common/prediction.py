from typing import List
from dataclasses import dataclass
from enum import Enum


class PredictionType(Enum):
    CLASSIFICATION = "classificationtype"
    CUSTOM = "customtype"


@dataclass
class PredictionDataDescriptor(object):
    prediction_data_type: PredictionType = None
