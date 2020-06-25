import docker
import time
import yaml
from io import StringIO

from thebox.common.connection import Connection
from thebox.db_couchdb.couchdb_repository_helper import CouchDbConnection, CouchDbRepositoryHelper


couchdb_test_config_content = """
image_name: 'couchdb:latest'
container_name: 'couchdb_unittest'
container_port: 5984
admin_user: 'admin'
admin_pass: 'ens_test'
"""

# Docker Python API documentation:
#  - https://docker-py.readthedocs.io/en/stable/
# CouchDB docker documentation
#  - https://docs.docker.com/samples/library/couchdb/#start-a-couchdb-instance


def setup_empty_test_db_server() -> Connection:
    '''
    Creates a test container of couchdb and return a connection object
    NOTES:
      - To access the DB content using Futon Web UI came with the CouchDB container, 
        go to following URL:
        http://localhost:5984/_utils/
    '''

    client = docker.from_env()
    # setup test couchdb
    couchdb_test_config = yaml.load(StringIO(couchdb_test_config_content))
    if couchdb_test_config['container_name'] not in [c.name for c in client.containers.list(all=True)]:
        print(
            f"creating test container '{couchdb_test_config['container_name']}' ...")
        client.containers.run(
            couchdb_test_config['image_name'],
            name=couchdb_test_config['container_name'],
            ports={'5984/tcp': couchdb_test_config['container_port']},
            environment={'COUCHDB_USER': couchdb_test_config['admin_user'],
                         'COUCHDB_PASSWORD': couchdb_test_config['admin_pass']},
            detach=True)
        # wait for container to launch successfully
        # hack: sleep 10 secs
        time.sleep(10)
        print("done.")
    elif couchdb_test_config['container_name'] not in [c.name for c in client.containers.list(all=False)]:
        client.containers.get(couchdb_test_config['container_name']).start()
    else:
        print(
            f"skip creating test container '{couchdb_test_config['container_name']}': already exist")

    return CouchDbConnection(
        f"http://localhost:{couchdb_test_config['container_port']}",
        couchdb_test_config['admin_user'],
        couchdb_test_config['admin_pass']
    )


def initialize_test_db(connection: Connection, db_name: str):
    c = CouchDbRepositoryHelper(connection, db_name)
    c.resetdb()
