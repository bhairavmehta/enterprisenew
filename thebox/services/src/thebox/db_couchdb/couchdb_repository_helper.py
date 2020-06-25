from typing import List, Dict
from copy import deepcopy
import jsonpickle
import json
from requests.adapters import HTTPAdapter
from cloudant.client import Cloudant
from cloudant.query import Query, QueryResult

from thebox.common.connection import Connection
from thebox.common.repository import RootObject


class CouchDbConnection(Connection):
    def __init__(self, url: str, user: str, token: str):
        self.url = url
        self.user = user
        self.token = token

    def __str__(self):
        return f"{self.url}, user={self.user}, pass=xxxx"


class CouchDbConnectionPool(object):
    """Static factory class that maintains the connection pool
    """
    connection_dict = dict()

    @staticmethod
    def get_client(connection: CouchDbConnection):
        if (connection.url, connection.user) not in CouchDbConnectionPool.connection_dict:
            conn = Cloudant(
                connection.user, connection.token,
                url=connection.url, connect=True,
                auto_renew=True)
            CouchDbConnectionPool.connection_dict[
                (connection.url, connection.user)] = conn
            return conn
        else:
            return CouchDbConnectionPool.connection_dict[
                (connection.url, connection.user)]


class CouchDbRepositoryHelper(object):

    def __init__(self, connection: CouchDbConnection, db_name: str):
        self.__client = CouchDbConnectionPool.get_client(connection)
        self.db_name = db_name
        self.__db = self.__create_db_if_not_exist(db_name)

    def __create_db_if_not_exist(self, db_name: str):
        if (db_name not in self.__client):
            return self.__client.create_database(db_name)
        else:
            return self.__client[db_name]

    def __delete_db_if_exist(self, db_name: str):
        if (db_name in self.__client):
            return self.__client.delete_database(db_name)

    def resetdb(self) -> None:
        """Recreate the database which would deletes all existing docs

        Returns:
            None
        """

        self.__delete_db_if_exist(self.db_name)
        self.__db = self.__create_db_if_not_exist(self.db_name)

    def serialize(self, ob: RootObject) -> str:
        """Serializes a given class object using jsonpickle and
           saving that into the current DB

        Arguments:
            ob {RootObject} -- object to be serialized

        Returns:
            str -- [description]
        """
        assert(isinstance(ob, RootObject))
        ob_cp = deepcopy(ob)
        ob_id = ob_cp._id
        ob_cp._id = None
        jsonstr = jsonpickle.encode(ob_cp)
        objson = json.loads(jsonstr)
        if ob_id is not None:
            objson['_id'] = ob_id
        doc = self.__db.create_document(objson)
        return doc['_id']

    def deserialize(self, ob_id: str) -> RootObject:
        """Load a document from DB and deserialize that into its
           original class object

        Arguments:
            ob_id {str} -- id of the document to be loaded from DB

        Returns:
            RootObject -- A document bearing the id being queried, or
               None if the document id is not valid
        """
        if ob_id in self.__db:
            # deferencing __db[id] returns cloudant.document.Document type
            objson = self.__db[ob_id].json()
            ob = jsonpickle.decode(objson)
            ob._id = ob_id
            return ob
        else:
            return None

    def deserialize_all(self) -> List[RootObject]:
        """Load all the documents from the current DB

        Returns:
            List[RootObject] -- A list of documents with base
                type of RootObject
        """
        res = []
        for doc in self.__db:
            ob = jsonpickle.decode(doc.json())
            ob._id = doc['_id']
            res.append(ob)
        return res

    def query(self, selector: Dict) -> List[RootObject]:
        """"query the db using selectors
        NOTE: {'_id': "doc id"} is currently not supported. Please
        use deserialize(self, ob_id: str) instead

        Arguments:
            selector {Dict} -- query selector. Example:
                {'scenario_name': {'$eq': 'test scenario'}}

        Returns:
            List[RootObject] -- A list of documents with base
                type of RootObject
        """
        selector_wrapped = {"py/state": selector}

        queryresult = self.__db.get_query_result(
            selector_wrapped,
            raw_result=True,
            limit=100
        )

        res = []
        for doc in queryresult['docs']:
            ob = jsonpickle.decode(json.dumps(doc))
            ob._id = doc['_id']
            res.append(ob)
        return res
