import os
import unittest
from collections import namedtuple

from unittest.mock import MagicMock
mymodule = MagicMock()
import sys
sys.modules["RPi"] = mymodule
from odie.actions.alphabot import AlphaBot
from odie.core.ActionModule import MissingParameterException

class TestAlphabot(unittest.TestCase):

    def setUp(self):
        self.Ab = AlphaBot()

    def test_init(self):
        try:
            mock.patch(self.ab.setMotor(0,0))
            return True
        except:
            return False

    def test_parameter_ok(self):
        with self.assertRaises(MissingParameterException):
            mock.patch(self.ab.setMove())

    def test_stop(self):
        try:
            mock.patch(self.ab.setMove('stop'))
            return True
        except:
            return False

     def test_forward(self):
        try:
            mock.patch(self.ab.setMove('forward'))
            return True
        except:
            return False

    def test_backward(self):
        try:
            mock.patch(self.ab.setMove('backward'))
            return True
        except:
            return False

    def test_left(self):
        try:
            mock.patch(self.ab.setMove('left'))
            return True
        except:
            return False

    def test_right(self):
        try:
            mock.patch(self.ab.setMove('right'))
            return True
        except:
            return False

    def test_right(self):
        try:
            mock.patch(self.ab.setMove('diagonal'))
            return False
        except:
            return True