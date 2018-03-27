import unittest
import sys
from mock import mock
from unittest.mock import MagicMock

from odie.actions.rover_initialise import Rover_initialise
from odie.actions.rover_set import Rover_set

from odie.core.ActionModule import MissingParameterException


mymodule = MagicMock()

sys.modules["RPi"] = mymodule


class TestAlphabot(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        try:
            mock.patch(Rover_initialise())
            return True
        except:
            return False

    def test_parameter_ok(self):
        with self.assertRaises(MissingParameterException):
            mock.patch(Rover_set())

    def test_stop(self):
        try:

            mock.patch(Rover_set('stop'))
            return True
        except:
            return False

    def test_forward(self):
        try:
            mock.patch(Rover_set('forward'))
            return True
        except:
            return False

    def test_backward(self):
        try:
            mock.patch(Rover_set('backward'))
            return True
        except:
            return False

    def test_left(self):
        try:
            mock.patch(Rover_set('left'))
            return True
        except:
            return False

    def test_right(self):
        try:
            mock.patch(Rover_set('right'))
            return True
        except:
            return False

    def test_invalid_direction(self):
        try:
            mock.patch(Rover_set('diagonal'))
            return False
        except:
            return True
