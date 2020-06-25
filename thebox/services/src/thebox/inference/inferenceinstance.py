from typing import List

import json
import pickle as pkl
from logging import Logger
import numpy as np

from thebox.common.scenario import InferenceDefinition
from thebox.common.model import ModelType, ModelIODescriptor, ModelDescriptor
from thebox.common_svc.logging import log_dump_truncate
from thebox.messages.inferencemessage import InferenceMessage, InferenceDataFeature
from thebox.messages.predictionmessage import PredictionMessage, PredictionData, ClassificationPredictionData, CustomPredictionData

from .modelcache import ModelCache
from .onnx_inference_provider import ONNXInferenceProvider
from .tensorflow_inference_provider import TensorFlowInferenceProvider

class InferenceServiceInstance(object):
    """Runs inference for on a specific scenario, which defines a specific module
       for a specific data source
    """

    def __init__(self, inf_def: InferenceDefinition, model_cache: ModelCache, log: Logger):
        """Initialize a new instance of inference service
           With a given scenario definition
        """
        assert(type(inf_def) is InferenceDefinition)
        assert(type(inf_def.model_descriptor) is ModelDescriptor)

        self.log = log
        self.model_cache = model_cache
        self.model_descriptor = inf_def.model_descriptor
        self.__load_model()

        self.log.debug(
            f"Created Inference Instance with model: {inf_def.model_descriptor.model_name}")

    def __load_model(self):
        model_file = self.model_cache.fetch_model(self.model_descriptor)
        if self.model_descriptor.model_type == ModelType.BUILTIN:
            raise NotImplementedError("model_type == ModelType.BUILTIN")
        else:
            model_type = self.model_descriptor.model_type
            if model_type == ModelType.ONNX:
                self.log.debug(f"Loading ONNX model {self.model_descriptor.model_name} from file {model_file} ...")
                prov = ONNXInferenceProvider(self.log)
            elif model_type == ModelType.TENSORFLOW:
                self.log.debug(f"Loading Tensorflow model {self.model_descriptor.model_name} from file {model_file} ...")
                prov = TensorFlowInferenceProvider(self.log)
            else:
                raise NotImplementedError(f"model_type == {model_type}")
            prov.load(model_file)
            self.model_provider = prov

    def run_inference(self, data: InferenceMessage) -> PredictionMessage:
        """Run the actual inference workload for a given inference data message
        """
        assert(isinstance(data, InferenceMessage))
        self.log.debug(f"Running inference for data with corr_id: {data.correlation_id}")
        assert(self.model_provider != None)

        # map features to a dictionary to be passed to ONNXRuntime
        input_features = self.model_descriptor.model_input_info
        input_feature_names = [ f.data_name for f in input_features ]
        
        input_dict = {}
        for f in data.feature_data:
            assert(isinstance(f, InferenceDataFeature))
            if f.feature_name not in input_feature_names:
                raise IndexError(f"Input feature '{f.feature_name}' is not defined on the model {self.model_descriptor.model_name}")
            # TODO: no check on the data type and dimenions yet
            input_dict[f.feature_name] = np.expand_dims(f.data, axis = 0)
            self.log.debug(f"Dimension of input ({f.feature_name}): {input_dict[f.feature_name].shape}")
        
        self.log.debug(f"Running inference on: {log_dump_truncate(input_dict)}")

        # obtain all output symbol names
        output_list = [ o.data_name for o in self.model_descriptor.model_output_info ]
        
        # run inference
        pred_results = self.model_provider.run(output_list, input_dict)
        self.log.debug(f"Result of inference: {log_dump_truncate(pred_results)}")
        
        # extract the results and pack into the PredictionMessage
        pred_data = { }
        for r in pred_results:
            d = CustomPredictionData(data=pred_results[r])
            # ToDo: this assertion is disable since some output of ONNX is not ndarray
            # we need to resolve this issue later
            # assert(isinstance(d.data, np.ndarray))
            pred_data[r] = d
        pred = PredictionMessage(data.correlation_id, pred_data)

        return pred
