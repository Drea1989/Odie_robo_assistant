import unittest

from mock import mock

from odie.core.ActionModule import MissingParameterException, InvalidParameterException
from odie.actions.neurotransmitter import Neurotransmitter


class TestNeurotransmitter(unittest.TestCase):

    def setUp(self):
        self.from_answer_link = [
            {
                "neuron": "neuron2",
                "answers": [
                    "answer one"
                ]
            },
            {
                "neuron": "neuron3",
                "answers": [
                    "answer two",
                    "answer three"
                ]
            },
        ]
        self.direct_link = "direct_link"
        self.default = "default"

    def testParameters(self):
        """
        Testing the Parameters checking
        """
        def run_test_invalid_parameter_exception(parameters_to_test):
            with self.assertRaises(InvalidParameterException):
                Neurotransmitter(**parameters_to_test)

        def run_test_missing_parameter_exception(parameters_to_test):
            with self.assertRaises(MissingParameterException):
                Neurotransmitter(**parameters_to_test)

        # empty
        parameters = dict()
        run_test_missing_parameter_exception(parameters)

        # missing direct_link and from_answer_link
        parameters = {
            "default": self.default
        }
        run_test_missing_parameter_exception(parameters)

        # missing direct_link and from_answer_link
        parameters = {
            "default": self.default,
            "from_answer_link": self.from_answer_link,
            "direct_link": self.direct_link
        }
        run_test_invalid_parameter_exception(parameters)

        # missing default
        parameters = {
            "from_answer_link": self.from_answer_link,
            "direct_link": self.direct_link
        }
        run_test_invalid_parameter_exception(parameters)

        # Missing answer in from_answer_link
        self.from_answer_link = [
            {
                "neuron": "neuron2",
            }
        ]

        parameters = {
            "default": self.default,
            "from_answer_link": self.from_answer_link
        }
        run_test_missing_parameter_exception(parameters)

        # Missing neuron in from_answer_link
        self.from_answer_link = [
            {
                "answer": "blablablbla",
            }
        ]

        parameters = {
            "default": self.default,
            "from_answer_link": self.from_answer_link
        }
        run_test_missing_parameter_exception(parameters)

    def testCallback(self):
        """
        Testing the callback provided when audio has been provided by the User as an answer.
        """
        parameters = {
            "default": self.default,
            "from_answer_link": self.from_answer_link
        }
        with mock.patch("odie.core.ActionModule.get_audio_from_stt") as mock_get_audio_from_stt:
            with mock.patch("odie.core.ActionModule.run_neuron_by_name") as mock_run_neuron_by_name:
                # testing running the default when no order matching
                nt = Neurotransmitter(**parameters)
                mock_get_audio_from_stt.assert_called_once()
                mock_get_audio_from_stt.reset_mock()

                # testing running the default when audio None
                audio_text = None
                nt.callback(audio=audio_text)
                mock_run_neuron_by_name.assert_called_once_with(self.default, high_priority=True, is_api_call=False)
                mock_run_neuron_by_name.reset_mock()

                # testing running the default when no order matching
                audio_text = "try test audio "
                nt.callback(audio=audio_text)
                mock_run_neuron_by_name.assert_called_once_with(self.default, high_priority=True, is_api_call=False)
                mock_run_neuron_by_name.reset_mock()

                # Testing calling the right neuron
                audio_text = "answer one"
                nt.callback(audio=audio_text)
                mock_run_neuron_by_name.assert_called_once_with(neuron_name="neuron2",
                                                                user_order=audio_text,
                                                                neuron_order="answer one",
                                                                high_priority=True,
                                                                is_api_call=False)

    def testInit(self):
        """
        Testing the init method of the actiontransmitter.
        """

        with mock.patch("odie.core.ActionModule.run_neuron_by_name") as mock_run_neuron_by_name:
            # Test direct link
            parameters = {
                "default": self.default,
                "direct_link": self.direct_link
            }
            Neurotransmitter(**parameters)
            mock_run_neuron_by_name.assert_called_once_with(self.direct_link, high_priority=True)

        with mock.patch("odie.core.ActionModule.get_audio_from_stt") as mock_get_audio_from_stt:
            # Test get_audio_from_stt
            parameters = {
                "default": self.default,
                "from_answer_link": self.from_answer_link,
            }
            Neurotransmitter(**parameters)
            mock_get_audio_from_stt.assert_called_once()


if __name__ == '__main__':
    unittest.main()
