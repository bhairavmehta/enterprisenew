from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name = 'thebox_notification',
      version = version,
      description = 'Notification Service for The Box',
      author = 'Jerry liang',
      author_email = 'jerrylia@microsoft.com',
      url = None,
      packages = [
            "thebox.common",
            "thebox.common_svc",
            "thebox.db_couchdb",
            "thebox.pubsub_kafka",
            "thebox.messages",
            "thebox.notification"
            ],
      package_dir={"": "src"},
      include_package_data = True,
      zip_safe = False,
      entry_points = {'service':['service = thebox.notification:main']},
      install_requires = [
                          'pyyaml',
                          'dataclasses',
                          'couchdb',
                          'cloudant',
                          'jsonpickle',
                          'confluent-kafka'
                          ],
      )