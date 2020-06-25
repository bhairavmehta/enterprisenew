import time
import uuid
from dataclasses import dataclass

from thebox.common.correlatable import Correlatable


@dataclass
class AbstractMessage(Correlatable):
    """This class is the root of all messages sending on the pubsub pipe
       for calls between microservices
    """

    def __post_init__(self):
        self.time_stamp = time.time()

    @classmethod
    def create_new_correlation_id(cls: type) -> str:
        """Helper method to generate a unique id for 
        message correlation
        
        Returns:
            [str] -- return the string format of the correlation id
        """
        return str(uuid.uuid4())