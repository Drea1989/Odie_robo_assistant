import unittest
from odie.core.Recordatio import Recordatio


class TestRecordatio(unittest.TestCase):

    def setUp(self):
        # cleanup the recordatio memory
        Recordatio.memory = dict()
        Recordatio.temp = dict()

    def test_get_memory(self):
        test_memory = {
            "key1": "value1",
            "key2": "value2"
        }

        Recordatio.memory = test_memory
        self.assertDictEqual(test_memory, Recordatio.get_memory())

    def test_save(self):
        key_to_save = "key1"
        value_to_save = "value1"

        expected_memory = {
             "key1": "value1"
        }

        Recordatio.save(key=key_to_save, value=value_to_save)
        self.assertDictEqual(expected_memory, Recordatio.memory)

    def test_get_from_key(self):
        test_memory = {
            "key1": "value1",
            "key2": "value2"
        }

        Recordatio.memory = test_memory
        expected_value = "value2"
        self.assertEqual(expected_value, Recordatio.get_from_key("key2"))

    def test_add_parameters_from_order(self):

        order_parameters = {
            "key1": "value1",
            "key2": "value2"
        }

        expected_temp_dict = {
            "key1": "value1",
            "key2": "value2"
        }

        Recordatio.add_parameters_from_order(order_parameters)
        self.assertDictEqual(Recordatio.temp, expected_temp_dict)

    def test_clean_parameter_from_order(self):
        Recordatio.temp = {
            "key1": "value1",
            "key2": "value2"
        }

        Recordatio.clean_parameter_from_order()
        expected_temp_dict = dict()
        self.assertDictEqual(expected_temp_dict, Recordatio.memory)

    def test_save_action_parameter_in_memory(self):

        # test with a list of parameter with bracket

        action1_parameters = {
            "key1": "value1",
            "key2": "value2"
        }

        dict_val_to_save = {"my_key_in_memory": "{{key1}}"}

        expected_dict = {"my_key_in_memory": "value1"}

        Recordatio.save_action_parameter_in_memory(odie_memory_dict=dict_val_to_save,
                                                   action_parameters=action1_parameters)

        self.assertDictEqual(expected_dict, Recordatio.memory)

        # test with a list of parameter with brackets and string
        self.setUp()  # clean
        action1_parameters = {
            "key1": "value1",
            "key2": "value2"
        }

        dict_val_to_save = {"my_key_in_memory": "string {{key1}}"}

        expected_dict = {"my_key_in_memory": "string value1"}

        Recordatio.save_action_parameter_in_memory(odie_memory_dict=dict_val_to_save,
                                                   action_parameters=action1_parameters)

        self.assertDictEqual(expected_dict, Recordatio.memory)

        # test with a list of parameter with only a string. Action parameters are not used
        self.setUp()  # clean
        action1_parameters = {
            "key1": "value1",
            "key2": "value2"
        }

        dict_val_to_save = {"my_key_in_memory": "string"}

        expected_dict = {"my_key_in_memory": "string"}

        Recordatio.save_action_parameter_in_memory(odie_memory_dict=dict_val_to_save,
                                                   action_parameters=action1_parameters)

        self.assertDictEqual(expected_dict, Recordatio.memory)

        # test with an empty list of parameter to save (no odie_memory set)
        self.setUp()  # clean

        action1_parameters = {
            "key1": "value1",
            "key2": "value2"
        }

        dict_val_to_save = None

        Recordatio.save_action_parameter_in_memory(odie_memory_dict=dict_val_to_save,
                                                   action_parameters=action1_parameters)

        self.assertDictEqual(dict(), Recordatio.memory)

    def test_save_parameter_from_order_in_memory(self):
        # Test with a value that exist in the temp memory
        order_parameters = {
            "key1": "value1",
            "key2": "value2"
        }

        Recordatio.temp = order_parameters

        dict_val_to_save = {"my_key_in_memory": "{{key1}}"}

        expected_dict = {"my_key_in_memory": "value1"}

        Recordatio.save_parameter_from_order_in_memory(dict_val_to_save)

        self.assertDictEqual(expected_dict, Recordatio.memory)

        # test with a value that does not exsit
        order_parameters = {
            "key1": "value1",
            "key2": "value2"
        }

        Recordatio.temp = order_parameters
        dict_val_to_save = {"my_key_in_memory": "{{key3}}"}

        self.assertFalse(Recordatio.save_parameter_from_order_in_memory(dict_val_to_save))


if __name__ == '__main__':
    unittest.main()
