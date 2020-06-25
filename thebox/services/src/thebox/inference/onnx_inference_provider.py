from typing import List, Dict

from logging import Logger
import numpy as np
import onnxruntime as ort

from thebox.common.scenario import InferenceDefinition
from thebox.common.model import ModelType, ModelIODescriptor, ModelDescriptor
from thebox.messages.inferencemessage import InferenceMessage, InferenceDataFeature
from thebox.messages.predictionmessage import PredictionMessage, PredictionData, ClassificationPredictionData

from .inference_provider import InferenceProvider

class ONNXInferenceProvider(InferenceProvider):
    """Using ONNXRuntime as underlying inference framework for running DL models
    """

    def __init__(self, logger: Logger):
        self.log = logger

    def load(self, model_file:str):
        """Load a model
        
        Arguments:
            model_file {str} -- The local cached model files that can be loaded
        """
        self.model = ort.InferenceSession(model_file)
        self.log.debug(f"Inputs:")
        for inp in self.model.get_inputs():
            self.log.debug(f"{inp.name}({inp.type}) - {inp.shape}")
        self.log.debug(f"Outputs:")
        for outp in self.model.get_outputs():
            self.log.debug(f"{outp.name}({outp.type}) - {outp.shape}")
        

    def run(self, output_list: List, input_dict: Dict):
        """Run inference using the model

        Arguments:
            output_list {List[Str]} -- A list of string representing the output symbol names
            input_dict {Dict[Str, NumPy]} -- A dictionary with input symbol name as key and NumPy array object as input to the model
        """
        assert(self.model is not None)
        assert(len(self.model.get_inputs()) == len(input_dict))
        assert(len(self.model.get_outputs()) == len(output_list))
        # run inference
        result = self.model.run(output_list, input_dict)

        return { r[0]:r[1] for r in zip(output_list, result) }
