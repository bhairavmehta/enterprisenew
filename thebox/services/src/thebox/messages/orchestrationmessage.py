from typing import List, Dict, TypeVar
from dataclasses import dataclass

from thebox.common.abstractmessage import AbstractMessage


@dataclass
class OrchestrationMessage(AbstractMessage):
    orchestration_data: object
