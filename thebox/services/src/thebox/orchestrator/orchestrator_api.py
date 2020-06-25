from typing import List, Optional
from dataclasses import field
from marshmallow_dataclass import dataclass
from flask import Flask, jsonify, request
from flask_restful_swagger import swagger
from flask_restful import Resource

from thebox.lib.mapper.object_mapper import ObjectMapper
from thebox.common.scenario import ScenarioDefinition, InferenceDefinition, NotificationDefinition, NotificationRule, PredictionDataDescriptor
from thebox.common.model import ModelType, DataType, ModelIODescriptor, ModelDescriptor

from .orchestrator_service import OrchestrationService
from .scenario import Scenario


@swagger.model
@dataclass
class IngestionDefinitionDto(object):
    in_topic: str = None
    out_topic: str = None
    data_descriptor: str = None


@swagger.model
@dataclass
class ModelIODescriptorDto(object):
    data_name: str = None
    data_type: str = None
    data_shape: List[int] = None

@swagger.model
@dataclass
class ModelDescriptorDto(object):
    model_type: str = None
    model_name: str = None
    model_input_info: List[ModelIODescriptorDto] = None
    model_output_info: List[ModelIODescriptorDto] = None
    model_location: str = None

@swagger.model
@dataclass
class PredictionDataDescriptorDto(object):
    prediction_data_type: str = None


@swagger.model
@dataclass
class InferenceDefinitionDto(object):
    in_topic: str = None
    out_topic: str = None
    model_descriptor: ModelDescriptorDto = None
    pred_type: PredictionDataDescriptorDto = None


@swagger.model
@dataclass
class NotificationRuleDto(object):
    rule_name: str = None
    rule_content: str = None
    notification_id: str = None


@swagger.model
@dataclass
class NotificationDefinitionDto(object):
    "Represents a NotificationDefinition object"
    in_topic: str = None
    out_topic: str = None
    rules: List[NotificationRuleDto] = None


@swagger.model
@dataclass
class ScenarioDefinitionDto(object):
    "Represents a ScenarioDefinition object"
    ingestion_definition: IngestionDefinitionDto = None
    inference_definition: InferenceDefinitionDto = None
    notification_definition: NotificationDefinitionDto = None


@swagger.model
@dataclass
class ScenarioDto(object):
    "Represents a Scenario object"
    _id: str = None
    scenario_name: str = None
    scenario_definition: ScenarioDefinitionDto = None


class OrchestrationServiceAPI(Resource):
    """API wrapper around Orchestration Service
    """
    #
    # initialize mappers
    #

    def createMap() -> ObjectMapper:
        mapper = ObjectMapper()
        # TODO:
        # create decorator to automatically do these mapping:
        # given an data class object, create its Dto correspondence and create object
        # mapper rule
        mapper.create_map(ScenarioDefinitionDto, ScenarioDefinition)
        mapper.create_map(ScenarioDefinition, ScenarioDefinitionDto)
        mapper.create_map(NotificationDefinitionDto, NotificationDefinition)
        mapper.create_map(NotificationDefinition, NotificationDefinitionDto)
        mapper.create_map(NotificationRuleDto, NotificationRule)
        mapper.create_map(NotificationRule, NotificationRuleDto)
        mapper.create_map(PredictionDataDescriptorDto,
                          PredictionDataDescriptor)
        mapper.create_map(PredictionDataDescriptor,
                          PredictionDataDescriptorDto)
        mapper.create_map(ModelIODescriptorDto, ModelIODescriptor, {'data_type': lambda o: DataType[o.data_type] })
        mapper.create_map(ModelIODescriptor, ModelIODescriptorDto, {'data_type': lambda o: o.data_type.name })
        mapper.create_map(ModelDescriptorDto, ModelDescriptor, {'model_type': lambda o: ModelType[o.model_type] })
        mapper.create_map(ModelDescriptor, ModelDescriptorDto, {'model_type': lambda o: o.model_type.name})
        mapper.create_map(InferenceDefinitionDto, InferenceDefinition)
        mapper.create_map(InferenceDefinition, InferenceDefinitionDto)
        mapper.create_map(ScenarioDto, Scenario, {'_id': lambda o: o._id })
        mapper.create_map(Scenario, ScenarioDto, {'_id': lambda o: o._id })
        return mapper

    objMapper = createMap()

    def __init__(self, svc: OrchestrationService):
        self.__svc = svc
        # object mapper initiation

    @swagger.operation(
        notes="Getting all the scenarios created",
        nickname='get'
    )
    def get(self):
        scns = self.__svc.get_scenarios()
        result = ScenarioDto.Schema(many=True).dump(
            [OrchestrationServiceAPI.objMapper.map(
                scn, ScenarioDto) for scn in scns]
        )
        return jsonify(result.data)

    @swagger.operation(
        notes="Creating a new scenario",
        nickname='put',
        parameters=[
            {
              "name": "body",
              "description": "",
              "required": True,
              "allowMultiple": False,
              "dataType": ScenarioDto.__name__,
              "paramType": "body"
            }
        ],
    )
    def put(self) -> None:
        scn_unmarshall = ScenarioDto.Schema().load(request.get_json())
        scn = OrchestrationServiceAPI.objMapper.map(
            scn_unmarshall.data, Scenario)
        #scnobj = scn_unmarshall.data
        #scn = Scenario(scnobj._id, scnobj.scenario_name, None)
        self.__svc.create_scenario(scn)
        return 201

    def delete(self, scenario_id: str) -> None:
        return 204
