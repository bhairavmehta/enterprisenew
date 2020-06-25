from typing import List
from dataclasses import dataclass

from thebox.common.abstractmessage import AbstractMessage


@dataclass
class InferenceDataFeature(object):
    feature_name: str
    data: object


@dataclass
class InferenceMessage(AbstractMessage):
    data_descriptor_name: str
    feature_data: List[InferenceDataFeature]
