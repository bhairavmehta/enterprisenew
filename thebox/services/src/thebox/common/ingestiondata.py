from typing import List
from dataclasses import dataclass
from enum import Enum


class FeatureType(Enum):
    STRING = "stringtype"
    NUMBER = "numerictype"
    ARRAY = "numpyarraytype"


@dataclass
class FeatureDescriptor(object):
    feature_name: str = None
    feature_type: FeatureType = None
    feature_params: str = None

    def __post_init__(self):
        self.check_type(self.feature_type)

    def check_type(self, feature_type: FeatureType):
        if (feature_type not in [FeatureType.STRING, FeatureType.NUMBER, FeatureType.ARRAY]):
            raise Exception(f"'{feature_type}' is not supported.")


@dataclass
class IngestionDataDescriptor(object):
    ingestion_data_name: str = None
    feature_list: List[FeatureDescriptor] = None
