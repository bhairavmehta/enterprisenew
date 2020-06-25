from typing import List
from dataclasses import dataclass

from thebox.common.scenario import InferenceDefinition
from thebox.common.repository import RootObject

@dataclass
class Inference(RootObject):
    inference_definition: InferenceDefinition = None
