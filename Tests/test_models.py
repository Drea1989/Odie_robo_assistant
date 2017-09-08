import unittest
import ast
import mock

from odie.core.Models.Player import Player
from odie.core.Models.Tts import Tts

from odie.core.Models.Wakeon import Wakeon

from odie.core.Models.Stt import Stt

from odie.core.Models.RestAPI import RestAPI

from odie.core.Models.Dna import Dna

from odie.core import LIFOBuffer
from odie.core.Models.Settings import Settings

from odie.core.Models import Action, Order, Neuron, Brain, Event, Resources, Singleton

from odie.core.Models.APIResponse import APIResponse
from odie.core.Models.MatchedNeuron import MatchedNeuron


class TestModels(unittest.TestCase):

    def setUp(self):
        # Kill the singleton
        Singleton._instances = dict()

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

        self.all_neuron_list1 = [self.neuron1,
                                  self.neuron2,
                                  self.neuron3]

        self.all_neuron_list2 = [self.neuron2,
                                  self.neuron3]

        self.brain_test1 = Brain(neurons=self.all_neuron_list1)
        self.brain_test2 = Brain(neurons=self.all_neuron_list2)
        # this brain is the same as the first one
        self.brain_test3 = Brain(neurons=self.all_neuron_list1)

        self.settings_test = Settings(default_neuron="Neuron3")

        # clean the LiFO
        LIFOBuffer.lifo_list = list()

    def test_APIResponse(self):
        user_order = "user order"
        self.matched_neuron = MatchedNeuron(matched_neuron=self.neuron1, matched_order=user_order)

        api_response = APIResponse()
        api_response.user_order = user_order
        api_response.list_processed_matched_neuron = [self.matched_neuron]

        expected_result_serialize = {
            'status': None,
            'matched_neurons':
                [
                    {
                        'matched_order': 'user order',
                        'action_module_list': [],
                        'neuron_name': 'Neuron1'
                    }
                ],
                'user_order': 'user order'
        }

        self.assertDictEqual(expected_result_serialize, api_response.serialize())

    def test_Brain(self):
        # test get neuron by name
        expect_result = self.neuron1
        neuron_name = "Neuron1"
        self.assertEqual(self.brain_test1.get_neuron_by_name(neuron_name), expect_result)

        # test equals
        self.assertTrue(self.brain_test1.__eq__(self.brain_test3))

        # test not equals
        self.assertFalse(self.brain_test1.__eq__(self.brain_test2))

    def test_Dna(self):
        # create DNA object
        dna1 = Dna(name="dna1", module_type="action", author="odie",
                   odie_supported_version="0.1", tags="test")

        dna2 = Dna(name="dna2", module_type="action", author="community",
                   odie_supported_version="0.1.2", tags="other")

        # this dna is exactly the same as the first one
        dna3 = Dna(name="dna1", module_type="action", author="odie",
                   odie_supported_version="0.1", tags="test")

        expected_result_serialize = {
            'odie_supported_version': '0.1',
            'tags': 'test',
            'type': 'action',
            'name': 'dna1',
            'author': 'odie'
        }

        self.assertDictEqual(expected_result_serialize, dna1.serialize())

        self.assertTrue(dna1.__eq__(dna3))
        self.assertFalse(dna1.__eq__(dna2))

    def test_Event(self):
        event1 = Event(year=2017, month=12, day=31, week=53, day_of_week=2,
                       hour=8, minute=30, second=0)

        event2 = Event(year=2018, month=11, day=30, week=25, day_of_week=4,
                       hour=9, minute=40, second=0)

        # same as the event1
        event3 = Event(year=2017, month=12, day=31, week=53, day_of_week=2,
                       hour=8, minute=30, second=0)

        expected_result_serialize = {
            'event': {
                'week': 53,
                'second': 0,
                'minute': 30,
                'hour': 8,
                'year': 2017,
                'day': 31,
                'day_of_week': 2,
                'month': 12
            }
        }

        self.assertDictEqual(expected_result_serialize, event1.serialize())

        self.assertTrue(event1.__eq__(event3))
        self.assertFalse(event1.__eq__(event2))

    def test_MatchedNeuron(self):
        user_order = "user order"
        matched_neuron1 = MatchedNeuron(matched_neuron=self.neuron1, matched_order=user_order)
        matched_neuron2 = MatchedNeuron(matched_neuron=self.neuron2, matched_order=user_order)
        matched_neuron3 = MatchedNeuron(matched_neuron=self.neuron1, matched_order=user_order)

        expected_result_serialize = {
            'matched_order': 'user order',
            'action_module_list': [],
            'neuron_name': 'Neuron1'
        }

        self.assertDictEqual(expected_result_serialize, matched_neuron1.serialize())

        self.assertTrue(matched_neuron1.__eq__(matched_neuron3))
        self.assertFalse(matched_neuron1.__eq__(matched_neuron2))

        # test action parameter loader is called
        with mock.patch("odie.core.ActionParameterLoader.get_parameters") as mock_get_parameters:

            MatchedNeuron(matched_neuron=self.neuron1, matched_order=user_order, user_order=user_order)
            mock_get_parameters.assert_called_once_with(neuron_order=user_order,
                                                        user_order=user_order)
            mock_get_parameters.reset_mock()

    def test_Action(self):

        action1 = Action(name="test", parameters={"key1": "val1", "key2": "val2"})
        action2 = Action(name="test", parameters={"key3": "val3", "key4": "val4"})
        action3 = Action(name="test", parameters={"key1": "val1", "key2": "val2"})

        expected_result_serialize = {'name': 'test', 'parameters': {'key2': 'val2', 'key1': 'val1'}}

        self.assertDictEqual(expected_result_serialize, action1.serialize())

        self.assertTrue(action1.__eq__(action3))
        self.assertFalse(action1.__eq__(action2))

        # test password
        action_name = "test"
        action_parameters = {
            "password": "my secret",
            "parameter": "test"
        }

        action = Action()
        action.name = action_name
        action.parameters = action_parameters

        expected_result_str = "{'name': 'test', 'parameters': {'password': '*****', 'parameter': 'test'}}"

        self.assertDictEqual(ast.literal_eval(action.__str__()), ast.literal_eval(expected_result_str))

        action_name = "test"
        action_parameters = {
            "password_parameter": "my secret",
            "parameter": "test"
        }

        action = Action()
        action.name = action_name
        action.parameters = action_parameters

        expected_result_str = "{'name': 'test', 'parameters': {'parameter': 'test', 'password_parameter': '*****'}}"

        self.assertDictEqual(ast.literal_eval(action.__str__()), ast.literal_eval(expected_result_str))

    def test_Order(self):
        order1 = Order(sentence="this is an order")
        order2 = Order(sentence="this is an other order")
        order3 = Order(sentence="this is an order")

        expected_result_serialize = {'order': 'this is an order'}
        expected_result_str = "{'order': 'this is an order'}"

        self.assertEqual(expected_result_serialize, order1.serialize())
        self.assertEqual(expected_result_str, order1.__str__())

        self.assertTrue(order1.__eq__(order3))
        self.assertFalse(order1.__eq__(order2))

    def test_Resources(self):
        resource1 = Resources(action_folder="/path/action", stt_folder="/path/stt",
                              tts_folder="/path/tts", wakeon_folder="/path/wakeon")

        resource2 = Resources(action_folder="/other_path/action", stt_folder="/other_path/stt",
                              tts_folder="/other_path/tts", wakeon_folder="/other_path/wakeon")

        resource3 = Resources(action_folder="/path/action", stt_folder="/path/stt",
                              tts_folder="/path/tts", wakeon_folder="/path/wakeon")

        expected_result_serialize = {
            'tts_folder': '/path/tts',
            'action_folder': '/path/action',
            'stt_folder': '/path/stt',
            'wakeon_folder': '/path/wakeon'
        }

        self.assertDictEqual(expected_result_serialize, resource1.serialize())

        self.assertTrue(resource1.__eq__(resource3))
        self.assertFalse(resource1.__eq__(resource2))

    def test_RestAPI(self):

        rest_api1 = RestAPI(password_protected=True, login="admin", password="password", active=True,
                            port=5000, allowed_cors_origin="*")

        rest_api2 = RestAPI(password_protected=False, active=False,
                            port=5000, allowed_cors_origin=None)

        rest_api3 = RestAPI(password_protected=True, login="admin", password="password", active=True,
                            port=5000, allowed_cors_origin="*")

        expected_result_serialize = {
            'password_protected': True,
            'port': 5000,
            'active': True,
            'allowed_cors_origin': '*',
            'password': 'password',
            'login': 'admin'
        }

        self.assertDictEqual(expected_result_serialize, rest_api1.serialize())

        self.assertTrue(rest_api1.__eq__(rest_api3))
        self.assertFalse(rest_api1.__eq__(rest_api2))

    def test_Settings(self):
        with mock.patch('platform.machine', return_value='pumpkins'):
            rest_api1 = RestAPI(password_protected=True,
                                login="admin",
                                password="password",
                                active=True,
                                port=5000, allowed_cors_origin="*")

            setting1 = Settings(default_tts_name="pico2wav",
                                default_stt_name="google",
                                default_wakeon_name="swoyboy",
                                default_player_name="mplayer",
                                ttss=["ttts"],
                                stts=["stts"],
                                random_wake_up_answers=["yes"],
                                random_wake_up_sounds=None,
                                play_on_ready_notification=False,
                                on_ready_answers=None,
                                on_ready_sounds=None,
                                wakeons=["snowboy"],
                                players=["mplayer"],
                                rest_api=rest_api1,
                                cache_path="/tmp/odie",
                                default_neuron="default_neuron",
                                resources=None,
                                variables={"key1": "val1"},
                                postgres=None,
                                alphabot=None)
            setting1.odie_version = "0.4.5"

            setting2 = Settings(default_tts_name="accapela",
                                default_stt_name="bing",
                                default_wakeon_name="swoyboy",
                                default_player_name="mplayer",
                                ttss=["ttts"],
                                stts=["stts"],
                                random_wake_up_answers=["no"],
                                random_wake_up_sounds=None,
                                play_on_ready_notification=False,
                                on_ready_answers=None,
                                on_ready_sounds=None,
                                wakeons=["snowboy"],
                                rest_api=rest_api1,
                                cache_path="/tmp/odie_tmp",
                                default_neuron="my_default_neuron",
                                resources=None,
                                variables={"key1": "val1"},
                                postgres=None,
                                alphabot=None)
            setting2.odie_version = "0.4.5"

            setting3 = Settings(default_tts_name="pico2wav",
                                default_stt_name="google",
                                default_wakeon_name="swoyboy",
                                default_player_name="mplayer",
                                ttss=["ttts"],
                                stts=["stts"],
                                random_wake_up_answers=["yes"],
                                random_wake_up_sounds=None,
                                play_on_ready_notification=False,
                                on_ready_answers=None,
                                on_ready_sounds=None,
                                wakeons=["snowboy"],
                                players=["mplayer"],
                                rest_api=rest_api1,
                                cache_path="/tmp/odie",
                                default_neuron="default_neuron",
                                resources=None,
                                variables={"key1": "val1"},
                                postgres=None,
                                alphabot=None)
            setting3.odie_version = "0.4.5"

            expected_result_serialize = {
                'default_tts_name': 'pico2wav',
                'default_stt_name': 'google',
                'default_wakeon_name': 'swoyboy',
                'default_player_name': 'mplayer',
                'ttss': ['ttts'],
                'stts': ['stts'],
                'random_wake_up_answers': ['yes'],
                'random_wake_up_sounds' : None,
                'play_on_ready_notification': False,
                'on_ready_answers': None,
                'on_ready_sounds': None,
                'wakeons': ['snowboy'],
                'players': ['mplayer'],
                'rest_api':
                    {
                        'password_protected': True,
                        'login': 'admin',
                        'password': 'password',
                        'active': True,
                        'port': 5000,
                        'allowed_cors_origin': '*'
                    },
                'cache_path': '/tmp/odie',
                'default_neuron': 'default_neuron',
                'resources': None,    
                'variables': {'key1': 'val1'},
                'machine': 'pumpkins',
                'odie_version': '0.4.5',
                'rpi_settings': None,
                'postgres':None,
                'alphabot':None
            }

            self.assertDictEqual(expected_result_serialize, setting1.serialize())

            self.assertTrue(setting1.__eq__(setting3))
            self.assertFalse(setting1.__eq__(setting2))

    def test_Stt(self):
        stt1 = Stt(name="stt1", parameters={"key1": "val1"})
        stt2 = Stt(name="stt2", parameters={"key2": "val2"})
        stt3 = Stt(name="stt1", parameters={"key1": "val1"})

        expected_result_serialize = {'name': 'stt1', 'parameters': {'key1': 'val1'}}

        self.assertDictEqual(expected_result_serialize, stt1.serialize())

        self.assertTrue(stt1.__eq__(stt3))
        self.assertFalse(stt1.__eq__(stt2))

    def test_Neuron(self):
        action1 = Action(name='actione1', parameters={'var1': 'val1'})
        action2 = Action(name='actione2', parameters={'var2': 'val2'})
        action3 = Action(name='actione3', parameters={'var3': 'val3'})
        action4 = Action(name='actione4', parameters={'var4': 'val4'})

        cue1 = Order(sentence="this is the sentence")
        cue2 = Order(sentence="this is the second sentence")

        neuron1 = Neuron(name="Neuron1", actions=[action1, action2], cues=[cue1])
        neuron2 = Neuron(name="Neuron2", actions=[action3, action4], cues=[cue2])
        neuron3 = Neuron(name="Neuron1", actions=[action1, action2], cues=[cue1])

        expected_result_serialize = {
            'cues': [
                {
                    'order': 'this is the sentence'
                }
            ],
            'actions': [
                {
                    'name': 'actione1',
                     'parameters': {
                         'var1': 'val1'
                     }
                },
                {
                    'name': 'actione2',
                    'parameters':
                        {
                            'var2': 'val2'
                        }
                }
            ],
            'name': 'Neuron1'
        }

        self.assertDictEqual(expected_result_serialize, neuron1.serialize())

        self.assertTrue(neuron1.__eq__(neuron3))
        self.assertFalse(neuron1.__eq__(neuron2))

    def test_Wakeon(self):
        wakeon1 = Wakeon(name="wakeon1", parameters={"key1": "val1"})
        wakeon2 = Wakeon(name="wakeon2", parameters={"key2": "val2"})
        wakeon3 = Wakeon(name="wakeon1", parameters={"key1": "val1"})

        expected_result_serialize = {'name': 'wakeon1', 'parameters': {'key1': 'val1'}}

        self.assertDictEqual(expected_result_serialize, wakeon1.serialize())

        self.assertTrue(wakeon1.__eq__(wakeon3))
        self.assertFalse(wakeon1.__eq__(wakeon2))

    def test_Player(self):
        player1 = Player(name="player1", parameters={"key1": "val1"})
        player2 = Player(name="player2", parameters={"key2": "val2"})
        player3 = Player(name="player1", parameters={"key1": "val1"})

        expected_result_serialize = {'name': 'player1', 'parameters': {'key1': 'val1'}}

        self.assertDictEqual(expected_result_serialize, player1.serialize())

        self.assertTrue(player1.__eq__(player3))
        self.assertFalse(player1.__eq__(player2))

    def test_Tts(self):
        tts1 = Tts(name="tts1", parameters={"key1": "val1"})
        tts2 = Tts(name="tts2", parameters={"key2": "val2"})
        tts3 = Tts(name="tts1", parameters={"key1": "val1"})

        expected_result_serialize = {'name': 'tts1', 'parameters': {'key1': 'val1'}}

        self.assertDictEqual(expected_result_serialize, tts1.serialize())

        self.assertTrue(tts1.__eq__(tts3))
        self.assertFalse(tts1.__eq__(tts2))


