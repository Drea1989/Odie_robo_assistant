import os
import unittest
import mock

from odie.core.Models import Singleton
from odie.core.Models.Tts import Tts

from odie import SettingLoader
from odie.core.ActionModule import ActionModule, TemplateFileNotFoundException, TTSModuleNotFound


class TestActionModule(unittest.TestCase):

    def setUp(self):
        # kill singleton
        Singleton._instances = dict()

        self.expected_result = "hello, this is a replaced word"
        # this allow us to run the test from an IDE and from the root with python -m unittest tests.TestActionModule
        if "/Tests" in os.getcwd():
            self.file_template = "templates/template_test.j2"
        else:
            self.file_template = "Tests/templates/template_test.j2"
        self.say_template = "hello, this is a {{ test }}"
        self.message = {
            "test": "replaced word"
        }
        self.action_module_test = ActionModule()

        if "/Tests" in os.getcwd():
            self.file_settings = "settings/settings_test.yml"
        else:
            self.file_settings = "Tests/settings/settings_test.yml"
        self.settings = SettingLoader(file_path=self.file_settings).settings

    def tearDown(self):
        del self.action_module_test

    def test_get_audio_from_stt(self):
        """
        Test the OrderListener thread is started
        """

        with mock.patch("odie.core.OrderListener.start") as mock_orderListener_start:
            with mock.patch("odie.core.OrderListener.join"):
                def callback():
                    pass

                self.action_module_test.get_audio_from_stt(callback=callback())
                mock_orderListener_start.assert_called_once_with()
                mock_orderListener_start.reset_mock()

    def test_get_tts_object(self):

        # no TTS name provided. should return the default tts
        expected_tts = Tts(name="pico2wave", parameters={"language": "en-US", "cache": True})
        self.assertEqual(ActionModule._get_tts_object(settings=self.settings), expected_tts)

        # TTS provided, only cache parameter updated
        expected_tts = Tts(name="pico2wave", parameters={"language": "en-US", "cache": False})
        self.assertEqual(ActionModule._get_tts_object(tts_name="pico2wave",
                                                      override_parameter={"cache": False},
                                                      settings=self.settings), expected_tts)

        # TTS provided, all parameters updated
        expected_tts = Tts(name="pico2wave", parameters={"language": "es-ES", "cache": False})
        self.assertEqual(ActionModule._get_tts_object(tts_name="pico2wave",
                                                      override_parameter={"language": "es-ES", "cache": False},
                                                      settings=self.settings), expected_tts)
        # TTS not existing in settings
        with self.assertRaises(TTSModuleNotFound):
            ActionModule._get_tts_object(tts_name="no_existing_tts",
                                         override_parameter={"cache": False},
                                         settings=self.settings)

    def test_get_message_from_dict(self):

        self.action_module_test.say_template = self.say_template

        self.assertEqual(self.action_module_test._get_message_from_dict(self.message), self.expected_result)
        del self.action_module_test
        self.action_module_test = ActionModule()

        # test with file_template
        self.action_module_test.file_template = self.file_template
        self.assertEqual(self.action_module_test._get_message_from_dict(self.message), self.expected_result)
        del self.action_module_test

        # test with no say_template and no file_template
        self.action_module_test = ActionModule()
        self.assertEqual(self.action_module_test._get_message_from_dict(self.message), None)

    def test_get_say_template(self):
        # test with a string
        self.assertEqual(ActionModule._get_say_template(self.say_template, self.message), self.expected_result)

        # test with a list
        say_template = list()
        say_template.append("hello, this is a {{ test }} one")
        say_template.append("hello, this is a {{ test }} two")
        expected_result = list()
        expected_result.append("hello, this is a replaced word one")
        expected_result.append("hello, this is a replaced word two")
        self.assertTrue(ActionModule._get_say_template(say_template, self.message) in expected_result)

    def test_get_file_template(self):
        # test with a valid template
        self.assertEqual(ActionModule._get_file_template(self.file_template, self.message), self.expected_result)

        # test raise with a non existing template
        file_template = "does_not_exist.j2"
        with self.assertRaises(TemplateFileNotFoundException):
            ActionModule._get_file_template(file_template, self.message)

    def test_get_content_of_file(self):
        expected_result = "hello, this is a {{ test }}"
        self.assertEqual(ActionModule._get_content_of_file(self.file_template), expected_result)

    def test_serialize(self):
        """
        Test the serialisation of the action module
        """
        action_module = ActionModule()
        action_module.action_name = "odie"
        action_module.tts_message = "I am italian"

        expected_result = {
            'action_name': "odie",
            'generated_message': "I am italian"
        }

        self.assertEqual(expected_result, action_module.serialize())


if __name__ == '__main__':
    unittest.main()
