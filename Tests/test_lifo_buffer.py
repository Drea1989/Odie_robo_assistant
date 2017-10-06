import os
import unittest

import mock

from odie.core import LIFOBuffer
from odie.core.ConfigurationManager import BrainLoader
from odie.core.LIFOBuffer import Serialize, NeuronListAddedToLIFO

from odie.core.Models import Singleton
from odie.core.Models.MatchedNeuron import MatchedNeuron


class TestLIFOBuffer(unittest.TestCase):

    def setUp(self):
        # be sure the brain haven't been instantiated before
        Singleton._instances = dict()

        if "/Tests" in os.getcwd():
            self.brain_to_test = os.getcwd() + os.sep + "brains/lifo_buffer_test_brain.yml"
        else:
            self.brain_to_test = os.getcwd() + os.sep + "Tests/brains/lifo_buffer_test_brain.yml"

        BrainLoader(file_path=self.brain_to_test)
        # create a new lifo buffer
        self.lifo_buffer = LIFOBuffer()
        self.lifo_buffer.clean()

    def test_execute(self):
        """
        In this test the brain contains a neurotransmitter
        """
        # --------------------------------------
        # Test 1. The user answers correctly to all neurotransmitter
        # --------------------------------------

        # we suppose that the first neuron has matched the first neuron
        neuron = BrainLoader().brain.get_neuron_by_name("neuron1")
        order = "enter in neuron 1"
        matched_neuron = MatchedNeuron(matched_neuron=neuron,
                                       user_order=order,
                                       matched_order=order)
        list_matched_neuron = list()
        list_matched_neuron.append(matched_neuron)
        self.lifo_buffer.add_neuron_list_to_lifo(list_matched_neuron)
        self.lifo_buffer.api_response.user_order = order

        with mock.patch("odie.core.TTS.TTSModule.generate_and_play"):

            response = self.lifo_buffer.execute(is_api_call=True)

            expected_result = {
                'status': 'waiting_for_answer',
                'matched_neurons': [
                    {
                        'matched_order': 'enter in neuron 1',
                        'action_module_list':
                            [
                                {
                                    'action_name': 'Say',
                                    'generated_message': 'question in neuron 1'
                                }
                            ],
                        'neuron_name': 'neuron1'
                    }
                ],
                'user_order': 'enter in neuron 1'
            }

            self.assertEqual(response, expected_result)

            # give an answer
            answer = "answer neuron1"
            response = self.lifo_buffer.execute(answer=answer,
                                                is_api_call=True)
            expected_result = {
                'status': 'waiting_for_answer',
                'matched_neurons': [
                    {
                        'matched_order': 'enter in neuron 1',
                        'action_module_list': [
                            {
                                'action_name': 'Say',
                                'generated_message': 'question in neuron 1'
                            },
                            {
                                'action_name': 'Neurotransmitter',
                                'generated_message': None
                            }
                        ],
                        'neuron_name': 'neuron1'
                    },
                    {
                        'matched_order': 'answer neuron1',
                        'action_module_list': [
                            {
                                'action_name': 'Say',
                                'generated_message': 'enter neuron 2'
                            }
                        ],
                        'neuron_name': 'neuron2'
                    }
                ],
                'user_order': None
            }
            self.assertEqual(response, expected_result)

            # give the last answer
            answer = "neuron5"
            response = self.lifo_buffer.execute(answer=answer,
                                                is_api_call=True)
            expected_result = {
                'status': 'complete',
                'matched_neurons': [
                    {
                        'matched_order': 'answer neuron1',
                        'action_module_list': [
                            {
                                'action_name': 'Say',
                                'generated_message': 'enter neuron 2'
                            },
                            {
                                'action_name': 'Neurotransmitter',
                                'generated_message': None
                            }
                        ],
                        'neuron_name': 'neuron2'
                    },
                    {
                        'matched_order': 'neuron5',
                        'action_module_list': [
                            {
                                'action_name': 'Say',
                                'generated_message': 'execution of neuron 5'
                            }
                        ],
                        'neuron_name': 'neuron5'
                    },
                    {
                        'matched_order': 'enter in neuron 1',
                        'action_module_list': [
                            {
                                'action_name': 'Say',
                                'generated_message': 'question in neuron 1'
                            },
                            {
                                'action_name': 'Neurotransmitter',
                                'generated_message': None
                            },
                            {
                                'action_name': 'Say',
                                'generated_message': 'last action in neuron 1'
                            }
                        ],
                        'neuron_name': 'neuron1'
                    }
                ],
                'user_order': None
            }

            self.assertEqual(response, expected_result)

        # --------------------------------------
        # Test 2. The user doesn't answer correctly to the first neurotransmitter
        # --------------------------------------

        # we suppose that the first neuron has matched the first neuron
        neuron = BrainLoader().brain.get_neuron_by_name("neuron1")
        order = "enter in neuron 1"
        matched_neuron = MatchedNeuron(matched_neuron=neuron,
                                       user_order=order,
                                       matched_order=order)
        list_matched_neuron = list()
        list_matched_neuron.append(matched_neuron)
        self.lifo_buffer.add_neuron_list_to_lifo(list_matched_neuron)
        self.lifo_buffer.api_response.user_order = order

        with mock.patch("odie.core.TTS.TTSModule.generate_and_play"):
            # fist call to enter in the neurotransmitter
            self.lifo_buffer.execute(is_api_call=True)

            wrong_answer = "wrong answer"
            response = self.lifo_buffer.execute(answer=wrong_answer, is_api_call=True)

            expected_result = {
                'status': 'complete',
                'matched_neurons': [
                    {
                        'matched_order': 'enter in neuron 1',
                        'action_module_list': [
                            {
                                'action_name': 'Say',
                                'generated_message': 'question in neuron 1'
                            },
                            {
                                'action_name': 'Neurotransmitter',
                                'generated_message': None
                            },
                            {
                                'action_name': 'Say',
                                'generated_message': 'last action in neuron 1'
                            }
                        ],
                        'neuron_name': 'neuron1'
                    },
                    {
                        'matched_order': None,
                        'action_module_list': [
                            {
                                'action_name': 'Say',
                                'generated_message': 'not understood'
                            }
                        ],
                        'neuron_name': 'neuron4'
                    }
                ],
                'user_order': None
            }

            self.assertEqual(response, expected_result)

        # --------------------------------------
        # Test 3. No neuron matched, we still execute the list
        # --------------------------------------
        list_matched_neuron = list()
        self.lifo_buffer.add_neuron_list_to_lifo(list_matched_neuron)
        self.lifo_buffer.api_response.user_order = "this is an order"

        with mock.patch("odie.core.TTS.TTSModule.generate_and_play"):
            # fist call to enter in the neurotransmitter
            response = self.lifo_buffer.execute(is_api_call=True)

            expected_result = {
                'status': None,
                'matched_neurons': [],
                'user_order': 'this is an order'
            }

            self.assertEqual(response, expected_result)

    def test_add_neuron_list_to_lifo(self):
        """
        Testing to add a neuron to the lifo
        """
        neuron = BrainLoader().brain.get_neuron_by_name("neuron1")
        order = "enter in neuron 1"
        matched_neuron = MatchedNeuron(matched_neuron=neuron,
                                       user_order=order,
                                       matched_order=order)
        list_matched_neuron = list()
        list_matched_neuron.append(matched_neuron)
        self.lifo_buffer.add_neuron_list_to_lifo(list_matched_neuron)

        self.assertEqual(self.lifo_buffer.lifo_list, [list_matched_neuron])

    def test_clean(self):
        """
        Test the Cleaning of the matched neurons list
        """
        neuron = BrainLoader().brain.get_neuron_by_name("neuron1")
        order = "enter in neuron 1"
        matched_neuron = MatchedNeuron(matched_neuron=neuron,
                                       user_order=order,
                                       matched_order=order)
        list_matched_neuron = list()
        list_matched_neuron.append(matched_neuron)
        self.lifo_buffer.add_neuron_list_to_lifo(list_matched_neuron)

        self.lifo_buffer.clean()
        self.assertEqual(0, len(self.lifo_buffer.lifo_list))

    def test_return_serialized_api_response(self):
        """
        Test the serialization
        """
        self.lifo_buffer.clean()
        self.lifo_buffer.execute(is_api_call=True)
        expected_result = {'status': None, 'matched_neurons': [], 'user_order': None}
        response = self.lifo_buffer._return_serialized_api_response()
        self.assertEqual(expected_result, response)

    def test_process_neuron_list(self):
        """
        Testing the action list from a neuron
        """
        neuron = BrainLoader().brain.get_neuron_by_name("neuron1")
        order = "enter in neuron 1"
        matched_neuron = MatchedNeuron(matched_neuron=neuron,
                                       user_order=order,
                                       matched_order=order)
        list_matched_neuron = list()
        list_matched_neuron.append(matched_neuron)

        with mock.patch("odie.core.LIFOBuffer._process_action_list"):
            self.lifo_buffer._process_neuron_list(list_matched_neuron)
            expected_response = {
                'status': None,
                'matched_neurons': [
                    {
                        'matched_order': 'enter in neuron 1',
                        'action_module_list': [],
                        'neuron_name': 'neuron1'
                    }
                ],
                'user_order': None
            }
            self.assertEqual(expected_response, self.lifo_buffer.api_response.serialize())
            self.assertEqual(0, len(self.lifo_buffer.lifo_list))

    def test_process_action_list(self):
        # Test with a action that doesn't wait for an answer
        neuron = BrainLoader().brain.get_neuron_by_name("neuron5")
        order = "neuron5"
        matched_neuron = MatchedNeuron(matched_neuron=neuron,
                                       user_order=order,
                                       matched_order=order)

        with mock.patch("odie.core.TTS.TTSModule.generate_and_play"):
            self.lifo_buffer.set_api_call(True)
            self.lifo_buffer._process_action_list(matched_neuron=matched_neuron)
            self.assertEqual("complete", self.lifo_buffer.api_response.status)

        # test with action that wait for an answer
        self.lifo_buffer.clean()
        neuron = BrainLoader().brain.get_neuron_by_name("neuron6")
        order = "neuron6"
        matched_neuron = MatchedNeuron(matched_neuron=neuron,
                                       user_order=order,
                                       matched_order=order)

        self.lifo_buffer.set_api_call(True)
        with mock.patch("odie.core.TTS.TTSModule.generate_and_play"):
            with self.assertRaises(Serialize):
                self.lifo_buffer._process_action_list(matched_neuron=matched_neuron)

        # test with a action that want to add a neuron list to the LIFO
        self.lifo_buffer.clean()
        neuron = BrainLoader().brain.get_neuron_by_name("neuron6")
        order = "neuron6"
        matched_neuron = MatchedNeuron(matched_neuron=neuron,
                                       user_order=order,
                                       matched_order=order)

        self.lifo_buffer.set_api_call(True)
        self.lifo_buffer.set_answer("neuron 6 answer")
        with mock.patch("odie.core.TTS.TTSModule.generate_and_play"):
            self.assertRaises(NeuronListAddedToLIFO,
                              self.lifo_buffer._process_action_list(matched_neuron=matched_neuron))


if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestSuite()
    # suite.addTest(TestLIFOBuffer("test_process_action_list"))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)
