import unittest
import logging

from thebox.common_svc.logging import setup_service_logger

class TestBase(unittest.TestCase):

    def setUp(self):
        print(
            f"Start TestCase: {self.__class__.__name__}:{self._testMethodName} -------------------")
        self.log = setup_service_logger(True)

    def tearDown(self):
        print(
            f"End TestCase: {self.__class__.__name__}:{self._testMethodName} ---------------------")
