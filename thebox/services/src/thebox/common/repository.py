from dataclasses import dataclass


class AbstractRepository(object):
    """Abstract Repository that defines commonly supported
       storage routines
    """

    def init(self) -> None:
        raise NotImplementedError("AbstractMethod Not Implemented")

    def load(self, id: str) -> object:
        raise NotImplementedError("AbstractMethod Not Implemented")

    def save(self, ob: object) -> str:
        raise NotImplementedError("AbstractMethod Not Implemented")


@dataclass
class RootObject(object):
    _id: str = None

    def __getstate__(self):
        """override for pickling support
        """
        state = self.__dict__.copy()
        if (state['_id'] == None):
            del state['_id']
        return state

    def __setstate__(self, state):
        """override for pickling support
        """
        self.__dict__.update(state)
