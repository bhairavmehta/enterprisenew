from typing import List
from dataclasses import dataclass

from thebox.common.scenario import NotificationDefinition
from thebox.common.repository import RootObject

@dataclass
class Notification(RootObject):
    notification_definition: NotificationDefinition = None
