from typing import List, Dict
from logging import Logger
import numpy as np

from thebox.common.scenario import InferenceDefinition
from thebox.common.model import ModelType, ModelIODescriptor, ModelDescriptor
from thebox.messages.inferencemessage import InferenceMessage, InferenceDataFeature
from thebox.messages.predictionmessage import PredictionMessage, PredictionData, ClassificationPredictionData


class InferenceProvider(object):
    """Provide inference APIs for a specific framework
    """

    def load(self, model_file:str):
        """Load a model
        
        Arguments:
            model_file {str} -- The local cached model files that can be loaded
        """
        pass

    def run(self, output_list: List, input_dict: Dict):
        """Run inference using the model

        Arguments:
            output_list {List[Str]} -- A list of string representing the output symbol names
            input_dict {Dict[Str, NumPy]} -- A dictionary with input symbol name as key and NumPy array object as input to the model
        """
        pass
