import unittest

from odie.core.ActionModule import MissingParameterException
from odie.actions.say.say import Say


class TestSay(unittest.TestCase):

    def setUp(self):
        self.message="message"
        self.random = "random"

    def testParameters(self):
        def run_test(parameters_to_test):
            with self.assertRaises(MissingParameterException):
                Say(**parameters_to_test)

        # empty
        parameters = dict()
        run_test(parameters)

        # missing message
        parameters = {
            "random": self.random
        }
        run_test(parameters)

