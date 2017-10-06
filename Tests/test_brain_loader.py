# coding: utf8
import os
import unittest

from odie.core.Models import Singleton, Cue

from odie.core.ConfigurationManager import BrainLoader
from odie.core.Models import Action
from odie.core.Models import Neuron
from odie.core.Models.Brain import Brain
from odie.core.Models.Settings import Settings


class TestBrainLoader(unittest.TestCase):

    def setUp(self):
        # be sure the brain haven't been instantiated before
        Singleton._instances = dict()
        if "/Tests" in os.getcwd():
            self.brain_to_test = os.getcwd() + os.sep + "brains/brain_test.yml"
        else:
            self.brain_to_test = os.getcwd() + os.sep + "Tests/brains/brain_test.yml"

        self.expected_result = [
            {'cues': [{'order': 'test_order'}],
             'actions': [{'say': {'message': ['test message']}}],
             'name': 'test'},
            {'cues': [{'order': 'test_order_2'}],
             'actions': [{'say': {'message': ['test message']}}],
             'name': 'test2'},
            {'cues': [{'order': 'order_for_int'}],
             'actions': [{'sleep': {'seconds': 60}}],
             'name': 'testint'},
            {'includes': ['included_brain_test.yml']},
            {'cues': [{'order': 'test_order_3'}],
             'actions': [{'say': {'message': ['test message']}}],
             'name': 'test3'}
        ]

    def tearDown(self):
        Singleton._instances = dict()

    def test_get_yaml_config(self):
        """
        Test we can get a yaml config from the path
        """
        brain_loader = BrainLoader(file_path=self.brain_to_test)
        self.assertEqual(brain_loader.yaml_config, self.expected_result)

    def test_get_brain(self):
        """
        Test the class return a valid brain object
        """

        action = Action(name='say', parameters={'message': ['test message']})
        action2 = Action(name='sleep', parameters={'seconds': 60})

        cue1 = Cue(name="order", parameters="test_order")
        cue2 = Cue(name="order", parameters="test_order_2")
        cue3 = Cue(name="order", parameters="test_order_3")
        cue4 = Cue(name="order", parameters="order_for_int")

        neuron1 = Neuron(name="test", actions=[action], cues=[cue1])
        neuron2 = Neuron(name="test2", actions=[action], cues=[cue2])
        neuron3 = Neuron(name="test3", actions=[action], cues=[cue3])
        neuron4 = Neuron(name="testint", actions=[action2], cues=[cue4])
        neurons = [neuron1, neuron2, neuron4, neuron3]

        brain = Brain()
        brain.neurons = neurons
        brain.brain_file = self.brain_to_test
        brain.brain_yaml = self.expected_result

        brain_loader = BrainLoader(file_path=self.brain_to_test)
        self.assertEqual(brain, brain_loader.brain)

    def test_get_actions(self):
        """
        Test to get actions from the brainLoader
        scenarii:
            - 1/ get a simple action from the brainloader
            - 2/ get a action with global variables as parameters
            - 3/ get a action with int as parameters
        """
        # 1/ get a simple action from the brainloader
        st = Settings()
        action_list = [{'say': {'message': ['test message']}}]

        action = Action(name='say', parameters={'message': ['test message']})

        bl = BrainLoader(file_path=self.brain_to_test)
        actions_from_brain_loader = bl._get_actions(action_list,
                                                    settings=st)

        self.assertEqual([action], actions_from_brain_loader)

        # 2/ get a action with global variables as parameters
        action_list = [{'say': {'message': ['bonjour {{name}}']}}]
        variables = {
            "author": "Lamonf",
            "test_number": 60,
            "name": "odie"
        }
        st = Settings(variables=variables)
        bl = BrainLoader(file_path=self.brain_to_test)
        actions_from_brain_loader = bl._get_actions(action_list,
                                                    settings=st)

        action = Action(name='say', parameters={'message': ['bonjour odie']})

        self.assertEqual([action], actions_from_brain_loader)

        # 3/ get a action with int as parameters
        st = Settings()
        action_list = [{'sleep': {'seconds': 60}}]

        action = Action(name='sleep', parameters={'seconds': 60})

        bl = BrainLoader(file_path=self.brain_to_test)
        actions_from_brain_loader = bl._get_actions(action_list,
                                                    settings=st)

        self.assertEqual([action], actions_from_brain_loader)

    def test_get_cues(self):
        cues = [{'order': 'test_order'}]

        cue = Cue(name="order", parameters="test_order")

        bl = BrainLoader(file_path=self.brain_to_test)
        cues_from_brain_loader = bl._get_cues(cues)

        self.assertEqual([cue], cues_from_brain_loader)

    '''
    def test_get_event_or_order_from_dict(self):

        order_object = Order(sentence="test_order")
        event_object = Event(hour="7")

        dict_order = {'order': 'test_order'}
        dict_event = {'event': {'hour': '7'}}

        bl = BrainLoader(file_path=self.brain_to_test)
        order_from_bl = bl._get_event_or_order_from_dict(dict_order)
        event_from_bl = bl._get_event_or_order_from_dict(dict_event)

        self.assertEqual(order_from_bl, order_object)
        self.assertEqual(event_from_bl, event_object)
    '''
    def test_singleton(self):
        bl1 = BrainLoader(file_path=self.brain_to_test)
        bl2 = BrainLoader(file_path=self.brain_to_test)

        self.assertTrue(bl1.brain is bl2.brain)

    def test_replace_global_variables(self):
        """
        Testing the _replace_global_variables function from the ActionLauncher.
        Scenarii:
            - 1/ only one global variable
            - 2/ global variable with string after
            - 3/ global variable with int after
            - 4/ multiple global variables
            - 5/ parameter value is a list
            - 6/ parameter is a dict

        """

        # 1/ only one global variable
        parameters = {
            'var1': '{{hello}}'
        }

        variables = {
            "hello": "test",
            "hello2": "test2",
        }
        st = Settings(variables=variables)

        expected_parameters = {
            'var1': 'test'
        }

        self.assertEqual(BrainLoader._replace_global_variables(parameter=parameters,
                                                               settings=st),
                         expected_parameters,
                         "Fail to assign a single global variable to parameters")

        # 2/ global variable with string after
        parameters = {
            'var1': '{{hello}} Sispheor'
        }
        variables = {
            "hello": "test",
            "hello2": "test2",
        }
        st = Settings(variables=variables)

        expected_parameters = {
            'var1': 'test Sispheor'
        }

        self.assertEqual(BrainLoader._replace_global_variables(parameter=parameters,
                                                               settings=st),
                         expected_parameters,
                         "Fail to assign a global variable with string after to parameters")

        # 3/ global variable with int after
        parameters = {
            'var1': '{{hello}}0'
        }
        variables = {
            "hello": 60,
            "hello2": "test2",
        }
        st = Settings(variables=variables)

        expected_parameters = {
            'var1': '600'
        }

        self.assertEqual(BrainLoader._replace_global_variables(parameter=parameters,
                                                               settings=st),
                         expected_parameters,
                         "Fail to assign global variable with int after to parameters")

        # 4/ multiple global variables
        parameters = {
            'var1': '{{hello}} {{me}}'
        }
        variables = {
            "hello": "hello",
            "me": "LaMonf"
        }
        st = Settings(variables=variables)

        expected_parameters = {
            'var1': 'hello LaMonf'
        }

        self.assertEqual(BrainLoader._replace_global_variables(parameter=parameters,
                                                               settings=st),
                         expected_parameters,
                         "Fail to assign multiple global variables to parameters")

        # 5/ parameter value is a list
        parameters = {
            'var1': '[hello {{name}}, bonjour {{name}}]'
        }
        variables = {
            "name": "LaMonf",
            "hello2": "test2",
        }
        st = Settings(variables=variables)

        expected_parameters = {
            'var1': '[hello LaMonf, bonjour LaMonf]'
        }

        self.assertEqual(BrainLoader._replace_global_variables(parameter=parameters,
                                                               settings=st),
                         expected_parameters,
                         "Fail to assign a single global when parameter value is a list to action")

        # 6/ parameter is a dict
        parameters = {'from_answer_link': [{'neuron': 'neuron2', 'answers': ['absolument', '{{ name }}']},
                                           {'neuron': 'neuron3', 'answers': ['{{ name }}']}], 'default': 'neuron4'}

        variables = {
            "name": "nico"
        }
        st = Settings(variables=variables)

        expected_parameters = {
            'from_answer_link': [
                {'neuron': 'neuron2', 'answers': ['absolument', 'nico']},
                {'neuron': 'neuron3', 'answers': ['nico']}], 'default': 'neuron4'
        }

        self.assertEqual(BrainLoader._replace_global_variables(parameter=parameters,
                                                               settings=st),
                         expected_parameters,
                         "Fail to assign a single global when parameter value is a list to action")

    def test_get_global_variable(self):
        """
        Test the get_global_variable of the OrderAnalyser Class
        """
        sentence = "i am {{name2}}"
        variables = {
            "name": "LaMonf",
            "name2": "odie",
            "name3": u"Odie",
            "name4": 1
        }
        st = Settings(variables=variables)

        expected_result = "i am odie"

        self.assertEqual(BrainLoader._get_global_variable(sentence=sentence,
                                                          settings=st),
                         expected_result)

        # test with accent
        sentence = "i am {{name3}}"
        expected_result = u"i am Odie"

        self.assertEqual(BrainLoader._get_global_variable(sentence=sentence,
                                                          settings=st),
                         expected_result)

        # test with int
        sentence = "i am {{name4}}"
        expected_result = "i am 1"

        self.assertEqual(BrainLoader._get_global_variable(sentence=sentence,
                                                          settings=st),
                         expected_result)


if __name__ == '__main__':
    unittest.main()
