from typing import List, Dict, TypeVar
from dataclasses import dataclass

from thebox.common.abstractmessage import AbstractMessage


@dataclass
class NotificationMessage(AbstractMessage):

    # name of the notification
    notification_id: str

    # custom data that came with the notification
    notification_data: str
