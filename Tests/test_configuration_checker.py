import unittest

from odie.core.ConfigurationManager.ConfigurationChecker import ConfigurationChecker, NoNeuronName, NoNeuronActions, \
    NoNeuronCues, NoValidCue, NoEventPeriod, NoValidOrder, MultipleSameNeuronName
from odie.core.Models import Neuron
from odie.core.Utils.Utils import ModuleNotFoundError


class TestConfigurationChecker(unittest.TestCase):
    """
    Class used to test the ConfigurationChecker class
    """

    def setUp(self):
        pass

    def test_check_neuron_dict(self):
        valid_neuron_dict = {
            'cues': [{'order': 'test_order'}],
            'actions': [{'say': {'message': ['test message']}}],
            'name': 'test'
        }

        neuron_dict_without_name = {
            'cues': [{'order': 'test_order'}],
            'actions': [{'say': {'message': ['test message']}}]
        }

        neuron_dict_without_actions = {
            'cues': [{'order': 'test_order'}],
            'name': 'test'
        }

        neuron_dict_without_cues = {
            'actions': [{'say': {'message': ['test message']}}],
            'name': 'test'
        }

        self.assertTrue(ConfigurationChecker.check_neuron_dict(valid_neuron_dict))

        with self.assertRaises(NoNeuronName):
            ConfigurationChecker.check_neuron_dict(neuron_dict_without_name)

        with self.assertRaises(NoNeuronActions):
            ConfigurationChecker.check_neuron_dict(neuron_dict_without_actions)

        with self.assertRaises(NoNeuronCues):
            ConfigurationChecker.check_neuron_dict(neuron_dict_without_cues)

    def test_check_action_dict(self):
        valid_action = {'say': {'message': ['test message']}}
        invalid_action = {'not_existing_action': {'message': ['test message']}}

        self.assertTrue(ConfigurationChecker.check_action_dict(valid_action))

        with self.assertRaises(ModuleNotFoundError):
            ConfigurationChecker.check_action_dict(invalid_action)

    def test_check_cue_dict(self):
        valid_cue_with_order = {'order': 'test_order'}
        valid_cue_with_event = {'event': '0 * * * *'}
        invalid_cue = {'invalid_option': 'test_order'}

        self.assertTrue(ConfigurationChecker.check_cue_dict(valid_cue_with_order))
        self.assertTrue(ConfigurationChecker.check_cue_dict(valid_cue_with_event))

        with self.assertRaises(NoValidCue):
            ConfigurationChecker.check_cue_dict(invalid_cue)

    def test_check_event_dict(self):
        valid_event = {
            "hour": "18",
            "minute": "16"
          }
        invalid_event = None
        invalid_event2 = ""
        invalid_event3 = {
            "notexisting": "12"
        }

        self.assertTrue(ConfigurationChecker.check_event_dict(valid_event))

        with self.assertRaises(NoEventPeriod):
            ConfigurationChecker.check_event_dict(invalid_event)
        with self.assertRaises(NoEventPeriod):
            ConfigurationChecker.check_event_dict(invalid_event2)
        with self.assertRaises(NoEventPeriod):
            ConfigurationChecker.check_event_dict(invalid_event3)

    def test_check_order_dict(self):
        valid_order = 'test_order'
        invalid_order = ''
        invalid_order2 = None

        self.assertTrue(ConfigurationChecker.check_order_dict(valid_order))

        with self.assertRaises(NoValidOrder):
            ConfigurationChecker.check_order_dict(invalid_order)
        with self.assertRaises(NoValidOrder):
            ConfigurationChecker.check_order_dict(invalid_order2)

    def test_check_neurons(self):
        neuron_1 = Neuron(name="test")
        neuron_2 = Neuron(name="test2")
        neuron_3 = Neuron(name="test")

        valid_neuron_list = [neuron_1, neuron_2]
        invalid_neuron_list = [neuron_1, neuron_3]

        self.assertTrue(ConfigurationChecker.check_neurons(valid_neuron_list))

        with self.assertRaises(MultipleSameNeuronName):
            ConfigurationChecker.check_neurons(invalid_neuron_list)


if __name__ == '__main__':
    unittest.main()
