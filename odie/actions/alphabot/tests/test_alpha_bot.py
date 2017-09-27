import os
import unittest
import sys
from collections import namedtuple
from mock import mock
from unittest.mock import MagicMock

import sys
from odie.actions.alphabot.initialiserover import Initialiserover
from odie.actions.alphabot.setrover import Setrover

from odie.core.ActionModule import MissingParameterException


mymodule = MagicMock()

sys.modules["RPi"] = mymodule


class TestAlphabot(unittest.TestCase):

    def setUp(self):
        pass

    def test_init(self):
        try:
            mock.patch(Initialiserover())
            return True
        except:
            return False

    def test_parameter_ok(self):
        with self.assertRaises(MissingParameterException):
            mock.patch(Setrover())

    def test_stop(self):
        try:

            mock.patch(Setrover('stop'))
            return True
        except:
            return False

    def test_forward(self):
        try:
            mock.patch(Setrover('forward'))
            return True
        except:
            return False

    def test_backward(self):
        try:
            mock.patch(Setrover('backward'))
            return True
        except:
            return False

    def test_left(self):
        try:
            mock.patch(Setrover('left'))
            return True
        except:
            return False

    def test_right(self):
        try:
            mock.patch(Setrover('right'))
            return True
        except:
            return False

    def test_right(self):
        try:
            mock.patch(Setrover('diagonal'))
            return False
        except:
            return True
