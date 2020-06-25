from typing import Dict, List
import yaml
import os


class ConfigurationError(BaseException):
    """Config related exception raised by this project
    """
    pass


class ConfigScenarioStore(object):
    def __init__(self, connection):
        self.connection = connection["connection"]
        self.username = connection["username"]
        self.usertoken = connection["usertoken"]


class ConfigEventQueue(object):
    def __init__(self, connection):
        self.connection = connection["server"]


class Config(object):
    """Configuration files consumed by services. Example format:

version: 1.0
store:
  couchdb:
    connection: "http://localhost:5984/"
    username: admin
    usertoken: ens_test
eventqueue:
  kafka:
    server: "http://localhost:9092"
servicesettings:
  orchestion_topic: orchestration_in_topic
    """

    CONFIG_PREFIX: str = "thebox_"

    def __init__(self, configFile: str = None, configString: str = None):

        if (configString is not None):
            self.__yamlDocs = yaml.load(configString, Loader=yaml.SafeLoader)
        else:
            with open(configFile, "r", encoding="utf-8") as f:
                self.__yamlDocs = yaml.load(f, Loader=yaml.SafeLoader)

        self.__load_os_environ_overrides()
        self.__validate_config()

    def __get_path(self, config_str: str) -> List[str]:
        return config_str.split("_")[1:]

    def __load_os_environ_overrides(self):
        os_overrides = {
            k.lower(): os.environ[k] for k in os.environ if k.lower().startswith(Config.CONFIG_PREFIX)
        }
        for k in os_overrides:
            path = self.__get_path(k)
            cur_dict = self.__yamlDocs
            for t_i in range(len(path)):
                t = path[t_i]
                if t_i == len(path) - 1:
                    if t in cur_dict and isinstance(cur_dict[t], Dict):
                        raise ConfigurationError(f"Value setting {k} has alraedy defined" +
                                                 f"as a config key that contains other values hence cannot be overriden")
                    cur_dict[t] = os_overrides[k]
                else:
                    if t not in cur_dict:
                        cur_dict[t] = dict()
                    cur_dict = cur_dict[t]

    def __validate_config(self):
        # TODO:
        #   more rigerous check
        invalid_sec = [sec for sec in self.__yamlDocs if sec not in [
            'version', 'store', 'eventqueue', 'servicesettings']]
        if len(invalid_sec):
            raise ConfigurationError(
                f"Unknown configuration section: {','.join(invalid_sec)}")

    def __getitem__(self, key: str):
        """Access config values using [key] operator
           This call support simplified way of access, e.g.:
              config['lvl1']['lvl2'] can also be accessed as config['lvl1.lvl2']
           It also handles when lvl1 doens't exist, it throws exception KeyError
        """
        path = key.split('.')
        cur_dict = self.__yamlDocs
        for t_i in range(len(path)):
            t = path[t_i]
            if t_i == len(path) - 1:
                return cur_dict[t]
            else:
                cur_dict = cur_dict[t]
        return None

    def try_get(self, key: str, default_val: str = None):
        """Same as [key] operator to access config value, except
           if key does not exist, it will not throw KeyError but
           instead consumes default_val value
        """
        try:
            val = self.__getitem__(key)
        except KeyError:
            val = default_val
        finally:
            return val

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.__yamlDocs}"
