import os
import unittest
from collections import namedtuple

from unittest.mock import MagicMock
mymodule = MagicMock()
import sys
sys.modules["RPi"] = mymodule
from odie.actions.alphabot import InitialiseRover, SetRover
from odie.core.ActionModule import MissingParameterException

class TestAlphabot(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        try:
            mock.patch(InitialiseRover())
            return True
        except:
            return False

    def test_parameter_ok(self):
        with self.assertRaises(MissingParameterException):
            mock.patch(SetRover())

    def test_stop(self):
        try:
            mock.patch(SetRover('stop'))
            return True
        except:
            return False

    def test_forward(self):
        try:
            mock.patch(SetRover('forward'))
            return True
        except:
            return False

    def test_backward(self):
        try:
            mock.patch(SetRover('backward'))
            return True
        except:
            return False

    def test_left(self):
        try:
            mock.patch(SetRover('left'))
            return True
        except:
            return False

    def test_right(self):
        try:
            mock.patch(SetRover('right'))
            return True
        except:
            return False

    def test_right(self):
        try:
            mock.patch(SetRover('diagonal'))
            return False
        except:
            return True