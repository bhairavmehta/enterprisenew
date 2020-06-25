from thebox.common.connection import Connection
from thebox.common.repository import AbstractRepository
from thebox.db_couchdb.couchdb_repository_helper import *

from .scenario import Scenario

class ScenarioRepository(AbstractRepository):

    def __init__(self, conn: Connection, db_name=None):
        if (db_name == None):
            db_name = "ScenarioRepository"
        self.__dbhelper = CouchDbRepositoryHelper(conn, db_name)

    def init(self) -> None:
        pass

    def load(self, id: str) -> Scenario:
        return self.__dbhelper.deserialize(id)

    def load_by_name(self, scenario_name: str) -> List[Scenario]:
        return self.__dbhelper.query({'scenario_name': {'$eq': scenario_name}})

    def load_all(self) -> List[Scenario]:
        return self.__dbhelper.deserialize_all()

    def save(self, ob: Scenario) -> str:
        return self.__dbhelper.serialize(ob)
