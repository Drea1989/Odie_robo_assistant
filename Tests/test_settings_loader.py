import os
import inspect
import platform
import shutil
import unittest

from odie.core.ConfigurationManager import SettingLoader
from odie.core.Models.RecognitionOptions import RecognitionOptions
from odie.core.Models import Singleton
from odie.core.Models import Resources
from odie.core.Models import Postgres, Cloud
from odie.core.Models.Player import Player
from odie.core.Models.RestAPI import RestAPI
from odie.core.Models.Settings import Settings
from odie.core.Models.Stt import Stt
from odie.core.Models.Wakeon import Wakeon
from odie.core.Models.Tts import Tts


class TestSettingLoader(unittest.TestCase):

    def setUp(self):
        # get current script directory path. We are in /an/unknown/path/odie/core/tests
        cur_script_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        # get parent dir. Now we are in /an/unknown/path/odie
        root_dir = os.path.normpath(cur_script_directory + os.sep + os.pardir)

        self.settings_file_to_test = root_dir + os.sep + "Tests/settings/settings_test.yml"

        self.settings_dict = {
            'default_neuron': 'Default-neuron',
            'rest_api':
                {'allowed_cors_origin': False,
                 'active': True,
                 'login': 'admin',
                 'password_protected': True,
                 'password': 'secret', 'port': 5000},
            'postgres':
                {'dbname': 'odie',
                 'user': 'admin',
                 'password': 'secret',
                 'host': 'localhost',
                 'port': 5432},
            'alphabot': {'enable': False},
            'cloud': {'category': 'speech', "parameters": {'model': '/tmp/model.pmld'}},
            'default_wakeon': 'snowboy',
            'default_player': 'mplayer',
            'play_on_ready_notification': 'never',
            'wakeons': [{'snowboy': {'pmdl_file': 'wakeon/snowboy/resources/odie-EN-1samples.pmdl'}}],
            'players': [{'mplayer': {}}, {'pyalsaaudio': {"device": "default"}}],
            'speech_to_text': [{'google': {'language': 'en-US'}}],
            'on_ready_answers': ['Odie is ready'],
            'cache_path': '/tmp/odie_tts_cache',
            'random_wake_up_answers': ['yes men?'],
            'on_ready_sounds': ['sounds/ding.wav', 'sounds/dong.wav'],
            'resource_directory': {
                'stt': '/tmp/odie/tests/odie_resources_dir/stt',
                'tts': '/tmp/odie/tests/odie_resources_dir/tts',
                'action': '/tmp/odie/tests/odie_resources_dir/actions',
                'wakeon': '/tmp/odie/tests/odie_resources_dir/wakeon'},
            'default_text_to_speech': 'pico2wave',
            'default_speech_to_text': 'google',
            'random_wake_up_sounds': ['sounds/ding.wav', 'sounds/dong.wav'],
            'text_to_speech': [
                {'pico2wave': {'cache': True, 'language': 'en-US'}},
                {'voxygen': {'voice': 'Agnes', 'cache': True}}],
            'var_files': ["../Tests/settings/variables.yml"]
        }

        # Init the folders, otherwise it raises an exceptions
        os.makedirs("/tmp/odie/tests/odie_resources_dir/actions")
        os.makedirs("/tmp/odie/tests/odie_resources_dir/stt")
        os.makedirs("/tmp/odie/tests/odie_resources_dir/tts")
        os.makedirs("/tmp/odie/tests/odie_resources_dir/wakeon")

    def tearDown(self):
        # Cleanup
        shutil.rmtree('/tmp/odie/tests/odie_resources_dir')

        Singleton._instances = {}

    def test_singleton(self):
        s1 = SettingLoader(file_path=self.settings_file_to_test)
        s2 = SettingLoader(file_path=self.settings_file_to_test)

        self.assertTrue(s1.settings is s2.settings)

    def test_get_yaml_config(self):

        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual(sl.yaml_config, self.settings_dict)

    def test_get_settings(self):
        settings_object = Settings()
        settings_object.default_tts_name = "pico2wave"
        settings_object.default_stt_name = "google"
        settings_object.default_wakeon_name = "snowboy"
        settings_object.default_player_name = "mplayer"
        tts1 = Tts(name="pico2wave", parameters={'cache': True, 'language': 'en-US'})
        tts2 = Tts(name="voxygen", parameters={'voice': 'Agnes', 'cache': True})
        settings_object.ttss = [tts1, tts2]
        stt = Stt(name="google", parameters={'language': 'en-US'})
        settings_object.stts = [stt]
        settings_object.random_wake_up_answers = ['yes men?']
        settings_object.random_wake_up_sounds = ['sounds/ding.wav', 'sounds/dong.wav']
        settings_object.play_on_ready_notification = "never"
        settings_object.on_ready_answers = ['Odie is ready']
        settings_object.on_ready_sounds = ['sounds/ding.wav', 'sounds/dong.wav']
        wakeon1 = Wakeon(name="snowboy",
                         parameters={'pmdl_file': 'wakeon/snowboy/resources/odie-EN-1samples.pmdl'})
        settings_object.wakeons = [wakeon1]
        player1 = Player(name="mplayer", parameters={})
        player2 = Player(name="pyalsaaudio", parameters={"device": "default"})
        settings_object.players = [player1, player2]
        settings_object.rest_api = RestAPI(password_protected=True, active=True,
                                           login="admin", password="secret", port=5000,
                                           allowed_cors_origin=False)
        settings_object.cache_path = '/tmp/odie_tts_cache'
        settings_object.default_neuron = 'Default-neuron'
        resources = Resources(action_folder="/tmp/odie/tests/odie_resources_dir/actions",
                              stt_folder="/tmp/odie/tests/odie_resources_dir/stt",
                              tts_folder="/tmp/odie/tests/odie_resources_dir/tts",
                              wakeon_folder="/tmp/odie/tests/odie_resources_dir/wakeon")
        settings_object.resources = resources
        settings_object.variables = {
            "author": "Andrea",
            "test_number": 60,
            "test": "odie"
        }
        settings_object.machine = platform.machine()
        settings_object.recognition_options = RecognitionOptions()
        postgres = Postgres(database='odie',
                            user='admin',
                            password='secret',
                            host='localhost',
                            port=5432)
        settings_object.postgres = postgres
        cl = Cloud(category='speech',
                   parameters={'model': '/tmp/model.pmld'})
        settings_object.cloud = cl
        settings_object.alphabot = {'enable': True}

        sl = SettingLoader(file_path=self.settings_file_to_test)

        self.assertEqual(settings_object, sl.settings)

    def test_get_default_speech_to_text(self):
        expected_default_speech_to_text = "google"
        sl = SettingLoader(file_path=self.settings_file_to_test)

        self.assertEqual(expected_default_speech_to_text, sl._get_default_speech_to_text(self.settings_dict))

    def test_get_default_text_to_speech(self):
        expected_default_text_to_speech = "pico2wave"
        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual(expected_default_text_to_speech, sl._get_default_text_to_speech(self.settings_dict))

    def test_get_default_wakeon(self):
        expected_default_wakeon = "snowboy"
        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual(expected_default_wakeon, sl._get_default_wakeon(self.settings_dict))

    def test_get_stts(self):
        stt = Stt(name="google", parameters={'language': 'en-US'})
        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual([stt], sl._get_stts(self.settings_dict))

    def test_get_ttss(self):
        tts1 = Tts(name="pico2wave", parameters={'cache': True, 'language': 'en-US'})
        tts2 = Tts(name="voxygen", parameters={'voice': 'Agnes', 'cache': True})
        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual([tts1, tts2], sl._get_ttss(self.settings_dict))

    def test_get_wakeons(self):
        wakeon1 = Wakeon(name="snowboy",
                         parameters={'pmdl_file': 'wakeon/snowboy/resources/odie-EN-1samples.pmdl'})
        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual([wakeon1], sl._get_wakeons(self.settings_dict))

    def test_get_players(self):
        player1 = Player(name="mplayer",
                         parameters={})
        player2 = Player(name="pyalsaaudio",
                         parameters={'device': 'default'})
        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual([player1, player2], sl._get_players(self.settings_dict))

    def test_get_random_wake_up_answers(self):
        expected_random_wake_up_answers = ['yes men?']
        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual(expected_random_wake_up_answers, sl._get_random_wake_up_answers(self.settings_dict))

    def test_get_on_ready_answers(self):
        expected_on_ready_answers = ['Odie is ready']
        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual(expected_on_ready_answers, sl._get_on_ready_answers(self.settings_dict))

    def test_get_on_ready_sounds(self):
        expected_on_ready_sounds = ['sounds/ding.wav', 'sounds/dong.wav']
        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual(expected_on_ready_sounds, sl._get_on_ready_sounds(self.settings_dict))

    def test_get_rest_api(self):
        expected_rest_api = RestAPI(password_protected=True, active=True,
                                    login="admin", password="secret", port=5000,
                                    allowed_cors_origin=False)

        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual(expected_rest_api, sl._get_rest_api(self.settings_dict))

    def test_get_cache_path(self):
        expected_cache_path = '/tmp/odie_tts_cache'
        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual(expected_cache_path, sl._get_cache_path(self.settings_dict))

    def test_get_default_neuron(self):
        expected_default_neuron = 'Default-neuron'
        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual(expected_default_neuron, sl._get_default_neuron(self.settings_dict))

    def test_get_resources(self):

        resources = Resources(action_folder="/tmp/odie/tests/odie_resources_dir/actions",
                              stt_folder="/tmp/odie/tests/odie_resources_dir/stt",
                              tts_folder="/tmp/odie/tests/odie_resources_dir/tts",
                              wakeon_folder="/tmp/odie/tests/odie_resources_dir/wakeon")
        expected_resource = resources
        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual(expected_resource, sl._get_resources(self.settings_dict))

    def test_get_variables(self):
        expected_result = {
            "author": "Andrea",
            "test_number": 60,
            "test": "odie"
        }
        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual(expected_result,
                         sl._get_variables(self.settings_dict))

    def test_get_postgres(self):
        expected_result = {'dbname': 'odie',
                           'user': 'admin',
                           'password': 'secret',
                           'host': 'localhost',
                           'port': 5432}
        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual(expected_result, sl._get_postgres(self.settings_dict))

    def test_get_alphabot(self):
        expected_result = {'enable': False}
        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual(expected_result, sl._get_alphabot(self.settings_dict))

    def test_get_cloud(self):
        expected_result = {'category': 'speech', "parameters": {'model': '/tmp/model.pmld'}}
        sl = SettingLoader(file_path=self.settings_file_to_test)
        self.assertEqual(expected_result, sl._get_cloud(self.settings_dict))


if __name__ == '__main__':
    unittest.main()
