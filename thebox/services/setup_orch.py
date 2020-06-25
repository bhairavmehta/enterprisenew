from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name = 'thebox_orchestrator',
      version = version,
      description = 'Orchestrator Service for The Box',
      author = 'Jerry liang',
      author_email = 'jerrylia@microsoft.com',
      url = None,
      packages = [
            "thebox.common",
            "thebox.common_svc",
            "thebox.db_couchdb",
            "thebox.pubsub_kafka",
            "thebox.messages",
            "thebox.lib.mapper",
            "thebox.orchestrator"
            ],
      package_dir={"": "src"},
      include_package_data = True,
      zip_safe = False,
      entry_points = {'service':['service = thebox.orchestrator:main']},
      install_requires = [
                          'pyyaml',
                          'dataclasses',
                          'couchdb',
                          'cloudant',
                          'jsonpickle',
                          'confluent-kafka',
                          'flask',
                          'flask-CORS',
                          'flask-restful-swagger',
                          'flask-marshmallow',
                          'marshmallow-dataclass'
                          ],
      )