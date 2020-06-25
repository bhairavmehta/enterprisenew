from dataclasses import dataclass
from enum import Enum
from typing import List


class ModelType(Enum):
    BUILTIN = "builtin"
    ONNX = "onnx"
    TENSORFLOW = "tensorflow"

class DataType(Enum):
    float32 = "float32"

@dataclass
class ModelIODescriptor(object):
    data_name: str = None
    data_type: DataType = None
    data_shape: List[int] = None

@dataclass
class ModelDescriptor(object):
    model_type: ModelType = None
    model_name: str = None
    model_input_info: List[ModelIODescriptor] = None
    model_output_info: List[ModelIODescriptor] = None
    model_class_labels: List[str] = None
    model_location: str = None
