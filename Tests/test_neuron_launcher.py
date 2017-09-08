import unittest

import mock

from odie.core import LIFOBuffer
from odie.core.Models import Brain
from odie.core.Models.MatchedNeuron import MatchedNeuron
from odie.core.Models.Settings import Settings
from odie.core.NeuronLauncher import NeuronLauncher, NeuronNameNotFound

from odie.core.Models import Action
from odie.core.Models import Order
from odie.core.Models import Neuron


class TestNeuronLauncher(unittest.TestCase):
    """
    Test the class NeuronLauncher
    """

    def setUp(self):
        # Init
        action1 = Action(name='actione1', parameters={'var1': 'val1'})
        action2 = Action(name='actione2', parameters={'var2': 'val2'})
        action3 = Action(name='actione3', parameters={'var3': 'val3'})
        action4 = Action(name='actione4', parameters={'var4': 'val4'})

        cue1 = Order(sentence="this is the sentence")
        cue2 = Order(sentence="this is the second sentence")
        cue3 = Order(sentence="that is part of the third sentence")

        self.neuron1 = Neuron(name="Neuron1", actions=[action1, action2], cues=[cue1])
        self.neuron2 = Neuron(name="Neuron2", actions=[action3, action4], cues=[cue2])
        self.neuron3 = Neuron(name="Neuron3", actions=[action2, action4], cues=[cue3])

        self.all_neuron_list = [self.neuron1,
                                 self.neuron2,
                                 self.neuron3]

        self.brain_test = Brain(neurons=self.all_neuron_list)
        self.settings_test = Settings(default_neuron="Neuron3")

        # clean the LiFO
        LIFOBuffer.lifo_list = list()

    def test_start_neuron_by_name(self):
        # existing neuron in the brain
        with mock.patch("odie.core.LIFOBuffer.execute"):
            should_be_created_matched_neuron = MatchedNeuron(matched_neuron=self.neuron1)
            NeuronLauncher.start_neuron_by_name("Neuron1", brain=self.brain_test)
            # we expect that the lifo has been loaded with the neuron to run
            expected_result = [[should_be_created_matched_neuron]]
            self.assertEqual(expected_result, LIFOBuffer.lifo_list)

        # non existing neuron in the brain
        with self.assertRaises(NeuronNameNotFound):
            NeuronLauncher.start_neuron_by_name("not_existing", brain=self.brain_test)

    def test_run_matching_neuron_from_order(self):
        # ------------------
        # test_match_neuron1
        # ------------------
        with mock.patch("odie.core.LIFOBuffer.execute"):
            order_to_match = "this is the sentence"

            should_be_created_matched_neuron = MatchedNeuron(matched_neuron=self.neuron1,
                                                               user_order=order_to_match,
                                                               matched_order="this is the sentence")
            expected_result = [[should_be_created_matched_neuron]]
            NeuronLauncher.run_matching_neuron_from_order(order_to_match,
                                                            brain=self.brain_test,
                                                            settings=self.settings_test)

            self.assertEqual(expected_result, LIFOBuffer.lifo_list)

        # -------------------------
        # test_match_neuron1_and_2
        # -------------------------
        # clean LIFO
        LIFOBuffer.lifo_list = list()
        with mock.patch("odie.core.LIFOBuffer.execute"):
            order_to_match = "this is the second sentence"
            should_be_created_matched_neuron1 = MatchedNeuron(matched_neuron=self.neuron1,
                                                                user_order=order_to_match,
                                                                matched_order="this is the sentence")
            should_be_created_matched_neuron2 = MatchedNeuron(matched_neuron=self.neuron2,
                                                                user_order=order_to_match,
                                                                matched_order="this is the second sentence")

            expected_result = [[should_be_created_matched_neuron1, should_be_created_matched_neuron2]]
            NeuronLauncher.run_matching_neuron_from_order(order_to_match,
                                                            brain=self.brain_test,
                                                            settings=self.settings_test)
            self.assertEqual(expected_result, LIFOBuffer.lifo_list)

        # -------------------------
        # test_match_default_neuron
        # -------------------------
        # clean LIFO
        LIFOBuffer.lifo_list = list()
        with mock.patch("odie.core.LIFOBuffer.execute"):
            order_to_match = "not existing sentence"
            should_be_created_matched_neuron = MatchedNeuron(matched_neuron=self.neuron3,
                                                               user_order=order_to_match,
                                                               matched_order=None)

            expected_result = [[should_be_created_matched_neuron]]
            NeuronLauncher.run_matching_neuron_from_order(order_to_match,
                                                            brain=self.brain_test,
                                                            settings=self.settings_test)
            self.assertEqual(expected_result, LIFOBuffer.lifo_list)

        # -------------------------
        # test_no_match_and_no_default_neuron
        # -------------------------
        # clean LIFO
        LIFOBuffer.lifo_list = list()
        with mock.patch("odie.core.LIFOBuffer.execute"):
            order_to_match = "not existing sentence"
            new_settings = Settings()
            expected_result = [[]]
            NeuronLauncher.run_matching_neuron_from_order(order_to_match,
                                                            brain=self.brain_test,
                                                            settings=new_settings)
            self.assertEqual(expected_result, LIFOBuffer.lifo_list)
