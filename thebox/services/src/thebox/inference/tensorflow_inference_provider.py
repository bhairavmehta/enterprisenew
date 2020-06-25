from typing import List, Dict

from logging import Logger
import numpy as np
import tensorflow as tf
from tensorflow.io.gfile import GFile

from thebox.common.scenario import InferenceDefinition
from thebox.common.model import ModelType, ModelIODescriptor, ModelDescriptor
from thebox.messages.inferencemessage import InferenceMessage, InferenceDataFeature
from thebox.messages.predictionmessage import PredictionMessage, PredictionData, ClassificationPredictionData

from .inference_provider import InferenceProvider

class TensorFlowInferenceProvider(InferenceProvider):
    """Using TensorFlow as underlying inference framework for running DL models
    """

    def __init__(self, logger: Logger):
        self.log = logger

    def load(self, model_file:str):
        """Load a model
        
        Arguments:
            model_file {str} -- The local cached model files that can be loaded
        """
        sess = tf.compat.v1.Session()
        
        self.log.debug(f"Loading frozen graph {model_file} as TF Graph ...")
        with GFile(model_file,'rb') as f:
            graph_def = tf.compat.v1.GraphDef()
            graph_def.ParseFromString(f.read())
            sess.graph.as_default()
            tf.import_graph_def(graph_def, name='')

        self.node_names = set([ n.name for n in graph_def.node ])
        self.log.debug("Graph loaded for the session.")
        self.sess = sess

        

    def run(self, output_list: List, input_dict: Dict):
        """Run inference using the model

        Arguments:
            output_list {List[Str]} -- A list of string representing the output symbol names
            input_dict {Dict[Str, NumPy]} -- A dictionary with input symbol name as key and NumPy array object as input to the model
        """
        assert(self.sess is not None)
        assert(all( k in self.node_names for k in input_dict ))
        assert(all( k in self.node_names for k in output_list ))
        
        tf_input = { f"{k}:0":input_dict[k] for k in input_dict }
        tf_output = [ f"{o}:0" for o in output_list ]

        # run inference
        self.log.debug(f"Input shape: {tf_input[list(tf_input.keys())[0]].shape}")
        result = self.sess.run(tf_output, tf_input)
        result_dict = { r[0]:r[1] for r in zip(output_list, result) }
        return result_dict
