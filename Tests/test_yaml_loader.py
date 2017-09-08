import os
import unittest

from odie.core.ConfigurationManager.YAMLLoader import YAMLFileNotFound, YAMLLoader


class TestYAMLLoader(unittest.TestCase):
    """
    Class to test YAMLLoader
    """

    def setUp(self):
        pass

    def test_get_config(self):

        if "/Tests" in os.getcwd():
            valid_file_path_to_test = os.getcwd() + os.sep + "brains/brain_test.yml"
        else:
            valid_file_path_to_test = os.getcwd() + os.sep + "Tests/brains/brain_test.yml"

        invalid_file_path = "brains/non_existing_brain.yml"
        expected_result = [
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

        with self.assertRaises(YAMLFileNotFound):
            YAMLLoader.get_config(invalid_file_path)

        self.assertEqual(YAMLLoader.get_config(valid_file_path_to_test), expected_result)


if __name__ == '__main__':
    unittest.main()
