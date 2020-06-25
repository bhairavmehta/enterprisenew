import unittest
import os

from thebox.common.config import Config, ConfigurationError

from .testbase import TestBase


class TestConfig(TestBase):

    def test_basic(self):
        dummy_config_file_name = "config.yaml.temp"
        dummy_config_file_text = """
        version: 1.0
        store:
          couchdb:
            connection: 'localhost:5984'
            username: fake
            usertoken: fake
        """
        with open(dummy_config_file_name, "w", encoding="utf-8") as dummy_config_file:
            print(dummy_config_file_text, file=dummy_config_file)
        c = Config(dummy_config_file_name)

        self.assertEqual(
            c['store']['couchdb']['connection'], 'localhost:5984')
        self.assertEqual(
            c['store.couchdb.connection'], 'localhost:5984')

    def test_override(self):
        dummy_config_file_text = """
        version: 1.0
        store:
          couchdb:
            connection: 'localhost:5984'
            username: fake
            usertoken: fake
        """
        os.environ["THEBOX_STORE_COUCHDB_USERNAME"] = "real"
        c = Config(None, dummy_config_file_text)
        del os.environ["THEBOX_STORE_COUCHDB_USERNAME"]

        self.assertEqual(
            c['store']['couchdb']['username'], 'real')
        self.assertEqual(
            c['store.couchdb.username'], 'real')
        self.assertEqual(
            c['store']['couchdb']['usertoken'], 'fake')
        self.assertEqual(
            c['store.couchdb.usertoken'], 'fake')

    def test_negative(self):
        dummy_config_file_text = """
        version: 1.0
        store:
          couchdb:
            connection: 'localhost:5984'
            username: fake
            usertoken: fake
        """
        c = Config(None, dummy_config_file_text)

        try:
            print(c['store.kafka.connection'])
            self.assertTrue(False)  # must not reach here
        except KeyError as e:
            self.assertIsNotNone(e)

        default_val = c.try_get('store.kafka.connection', 'default_value')
        self.assertEqual(default_val, "default_value")


if __name__ == '__main__':
    unittest.main()
