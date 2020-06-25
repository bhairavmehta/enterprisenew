
from typing import List
from dataclasses import dataclass


@dataclass
class Correlatable(object):
    """Correlatable is the base class for data object that
       carries a correlation id. Used by data processing
       and debugging
    """
    correlation_id: str
