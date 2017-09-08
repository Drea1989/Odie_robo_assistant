# coding: utf-8

import unittest
import mock

from odie.core.Models.Resources import Resources
from odie.core.ActionLauncher import ActionLauncher, ActionParameterNotAvailable
from odie.core.ConfigurationManager import SettingLoader

from odie.core.Models.Action import Action


class TestActionLauncher(unittest.TestCase):
    """
    Class to test Launchers Classes (WakeonLauncher, NeuronLauncher, ActionLauncher) and methods
    """

    def setUp(self):
        pass

    ####
    # Actions Launcher
    def test_launch_action(self):
        """
        Test the Action Launcher trying to start a Action
        """
        action = Action(name='actione1', parameters={'var1': 'val1'})
        sl = SettingLoader()
        resources = Resources(action_folder='/var/tmp/test/resources')
        sl.settings.resources = resources
        with mock.patch("odie.core.Utils.get_dynamic_class_instantiation") as mock_get_class_instantiation:
            ActionLauncher.launch_action(action=action)

            mock_get_class_instantiation.assert_called_once_with(package_name="actions",
                                                                 module_name=action.name,
                                                                 parameters=action.parameters,
                                                                 resources_dir=sl.settings.resources.action_folder)
            mock_get_class_instantiation.reset_mock()

    def test_start_action(self):
        """
        Testing params association and starting a Action
        """

        with mock.patch("odie.core.ActionLauncher.launch_action") as mock_launch_action_method:
            # Assert to the action is launched with not parameter from order
            action1 = Action(name='actione1', parameters={'var1': 'val1'})

            ActionLauncher.start_action(action=action1)
            mock_launch_action_method.assert_called_with(action1)
            mock_launch_action_method.reset_mock()

            # Assert the params are well passed to the action
            action2 = Action(name='actione2', parameters={'var2': 'val2', 'var3': "{{ var3 }}"})
            params = {
                'var3': 'value3'
            }
            ActionLauncher.start_action(action=action2,
                                        parameters_dict=params)
            action2_params = Action(name='actione2', parameters={'var2': 'val2', 'var3': 'value3'})

            mock_launch_action_method.assert_called_with(action2_params)
            mock_launch_action_method.reset_mock()

            # Assert the Action is not started when missing args
            action3 = Action(name='actione3', parameters={'var3': 'val3', 'var4': '{{val4}}'})
            params = {
                'not_exist': 'test'
            }
            ActionLauncher.start_action(action=action3,
                                        parameters_dict=params)
            mock_launch_action_method.assert_not_called()
            mock_launch_action_method.reset_mock()

            # Assert no action is launched when waiting for args and none are given
            action4 = Action(name='actione4', parameters={'var5': 'val5', 'var6': '{{val6}}'})

            ActionLauncher.start_action(action=action4)
            mock_launch_action_method.assert_not_called()
            mock_launch_action_method.reset_mock()

    def test_replace_brackets_by_loaded_parameter(self):
        # -------------------
        # test with string
        # -------------------
        # the target value to replace is present in the loaded parameter dict
        action_parameters = {
            "param1": "this is a value {{ replaced }}"
        }

        loaded_parameters = {
            "replaced": "replaced successfully"
        }

        expected_result = {
            "param1": "this is a value replaced successfully"
        }

        self.assertEqual(expected_result, ActionLauncher._replace_brackets_by_loaded_parameter(action_parameters,
                                                                                               loaded_parameters))

        # the target value with unicode to replace is present in the loaded parameter dict
        action_parameters = {
            "param1": "this is a value {{ replaced }}"
        }

        loaded_parameters = {
            "replaced": u"rêmpläcée successfülly"
        }

        expected_result = {
            "param1": "this is a value rêmpläcée successfülly"
        }

        self.assertEqual(expected_result, ActionLauncher._replace_brackets_by_loaded_parameter(action_parameters,
                                                                                               loaded_parameters))

        # the target value to replace is NOT present in the loaded parameter dict
        action_parameters = {
            "param1": "this is a value {{ replaced }}"
        }

        loaded_parameters = {
            "not_exist": "replaced successfully"
        }

        with self.assertRaises(ActionParameterNotAvailable):
            ActionLauncher._replace_brackets_by_loaded_parameter(action_parameters, loaded_parameters)

        # one parameter doesn't contains bracket, the other one do
        action_parameters = {
            "param1": "this is a value {{ replaced }}",
            "param2": "value"
        }

        loaded_parameters = {
            "replaced": "replaced successfully"
        }

        expected_result = {
            "param1": "this is a value replaced successfully",
            "param2": "value"
        }

        self.assertEqual(expected_result, ActionLauncher._replace_brackets_by_loaded_parameter(action_parameters,
                                                                                               loaded_parameters))

        # parameters are integer or boolean
        action_parameters = {
            "param1": 1,
            "param2": True
        }

        loaded_parameters = {
            "replaced": "replaced successfully"
        }

        expected_result = {
            "param1": 1,
            "param2": True
        }

        self.assertEqual(expected_result, ActionLauncher._replace_brackets_by_loaded_parameter(action_parameters,
                                                                                               loaded_parameters))

        # parameters are say_template or file template. Should not be altered by the loader
        action_parameters = {
            "say_template": "{{output}}",
            "file_template": "here is a file"
        }

        loaded_parameters = {
            "output": "should not be used"
        }

        expected_result = {
            "say_template": "{{output}}",
            "file_template": "here is a file"
        }

        self.assertEqual(expected_result, ActionLauncher._replace_brackets_by_loaded_parameter(action_parameters,
                                                                                               loaded_parameters))

    def test_parameters_are_available_in_loaded_parameters(self):
        # the parameter in bracket is available in the dict
        string_parameters = "this is a {{ parameter1 }}"
        loaded_parameters = {"parameter1": "value"}

        self.assertTrue(ActionLauncher._action_parameters_are_available_in_loaded_parameters(string_parameters,
                                                                                            loaded_parameters))

        # the parameter in bracket is NOT available in the dict
        string_parameters = "this is a {{ parameter1 }}"
        loaded_parameters = {"parameter2": "value"}

        self.assertFalse(ActionLauncher._action_parameters_are_available_in_loaded_parameters(string_parameters,
                                                                                             loaded_parameters))

        # the string_parameters doesn't contains bracket in bracket is available in the dict
        string_parameters = "this is a {{ parameter1 }}"
        loaded_parameters = {"parameter1": "value"}

        self.assertTrue(ActionLauncher._action_parameters_are_available_in_loaded_parameters(string_parameters,
                                                                                            loaded_parameters))

        # the string_parameters contains 2 parameters available in the dict
        string_parameters = "this is a {{ parameter1 }} and this is {{ parameter2 }}"
        loaded_parameters = {"parameter1": "value", "parameter2": "other value"}

        self.assertTrue(ActionLauncher._action_parameters_are_available_in_loaded_parameters(string_parameters,
                                                                                            loaded_parameters))

        # the string_parameters contains 2 parameters and one of them is not available in the dict
        string_parameters = "this is a {{ parameter1 }} and this is {{ parameter2 }}"
        loaded_parameters = {"parameter1": "value", "parameter3": "other value"}

        self.assertFalse(ActionLauncher._action_parameters_are_available_in_loaded_parameters(string_parameters,
                                                                                             loaded_parameters))


if __name__ == '__main__':
    unittest.main()

    # suite = unittest.TestSuite()
    # suite.addTest(TestActionLauncher("test_start_action"))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)
