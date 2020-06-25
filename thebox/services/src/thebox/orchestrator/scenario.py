from typing import List
from dataclasses import dataclass

from thebox.common.scenario import ScenarioDefinition
from thebox.common.repository import RootObject

@dataclass
class Scenario(RootObject):
    scenario_name: str = None
    scenario_definition: ScenarioDefinition = None
