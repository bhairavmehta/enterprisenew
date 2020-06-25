from typing import List

from thebox.common.connection import Connection
from thebox.common.repository import AbstractRepository
from thebox.common.scenario import *
from thebox.db_couchdb.couchdb_repository_helper import *

from .inference_object import Inference

class InferenceDefinitionRepository(AbstractRepository):

    def __init__(self, conn: Connection, db_name=None):
        if (db_name == None):
            db_name = "InferenceDefinitionRepository"
        self.__dbhelper = CouchDbRepositoryHelper(conn, db_name)

    def load(self, id: str) -> InferenceDefinition:
        return self.__dbhelper.deserialize(id)

    def load_all(self) -> List[InferenceDefinition]:
        return self.__dbhelper.deserialize_all()

    def save(self, ob: InferenceDefinition) -> str:
        return self.__dbhelper.serialize(ob)
