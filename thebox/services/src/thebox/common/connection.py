from dataclasses import dataclass


@dataclass
class Connection(object):
    """Abstract class of a connection object
    """
    # type name of the connection
    connection_type: str
