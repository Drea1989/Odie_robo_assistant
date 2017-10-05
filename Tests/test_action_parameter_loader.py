import unittest

from odie.core.ActionParameterLoader import ActionParameterLoader


class TestActionParameterLoader(unittest.TestCase):

    def test_get_parameters(self):

        neuron_order = "this is the {{ sentence }}"
        user_order = "this is the value"
        expected_result = {'sentence': 'value'}

        self.assertEqual(ActionParameterLoader.get_parameters(neuron_order=neuron_order, user_order=user_order),
                         expected_result,
                         "Fail to retrieve 'the params' of the neuron_order from the order")

        # Multiple match
        neuron_order = "this is the {{ sentence }}"

        user_order = "this is the value with multiple words"
        expected_result = {'sentence': 'value with multiple words'}

        self.assertEqual(ActionParameterLoader.get_parameters(neuron_order=neuron_order, user_order=user_order),
                         expected_result,
                         "Fail to retrieve the 'multiple words params' of the neuron_order from the order")

        # Multiple params
        neuron_order = "this is the {{ sentence }} with multiple {{ params }}"

        user_order = "this is the value with multiple words"
        expected_result = {'sentence': 'value',
                           'params':'words'}

        self.assertEqual(ActionParameterLoader.get_parameters(neuron_order=neuron_order, user_order=user_order),
                         expected_result,
                         "Fail to retrieve the 'multiple params' of the neuron_order from the order")

        # Multiple params with multiple words
        neuron_order = "this is the {{ sentence }} with multiple {{ params }}"

        user_order = "this is the multiple values with multiple values as words"
        expected_result = {'sentence': 'multiple values',
                           'params': 'values as words'}

        self.assertEqual(ActionParameterLoader.get_parameters(neuron_order=neuron_order, user_order=user_order),
                         expected_result)

        # params at the begining of the sentence
        neuron_order = "{{ sentence }} this is the sentence"

        user_order = "hello world this is the multiple values with multiple values as words"
        expected_result = {'sentence': 'hello world'}

        self.assertEqual(ActionParameterLoader.get_parameters(neuron_order=neuron_order, user_order=user_order),
                         expected_result)

        # all of the sentence is a variable
        neuron_order = "{{ sentence }}"

        user_order = "this is the all sentence is a variable"
        expected_result = {'sentence': 'this is the all sentence is a variable'}

        self.assertEqual(ActionParameterLoader.get_parameters(neuron_order=neuron_order, user_order=user_order),
                         expected_result)

    def test_associate_order_params_to_values(self):
        ##
        # Testing the brackets position behaviour
        ##

        # Success
        order_brain = "This is the {{ variable }}"
        order_user = "This is the value"
        expected_result = {'variable': 'value'}
        self.assertEqual(ActionParameterLoader._associate_order_params_to_values(order_user, order_brain),
                         expected_result)

        # Success
        order_brain = "This is the {{variable }}"
        order_user = "This is the value"
        expected_result = {'variable': 'value'}
        self.assertEqual(ActionParameterLoader._associate_order_params_to_values(order_user, order_brain),
                         expected_result)

        # Success
        order_brain = "This is the {{ variable}}"
        order_user = "This is the value"
        expected_result = {'variable': 'value'}
        self.assertEqual(ActionParameterLoader._associate_order_params_to_values(order_user, order_brain),
                         expected_result)

        # Success
        order_brain = "This is the {{variable}}"
        order_user = "This is the value"
        expected_result = {'variable': 'value'}
        self.assertEqual(ActionParameterLoader._associate_order_params_to_values(order_user, order_brain),
                         expected_result)

        # Fail
        order_brain = "This is the {variable}"
        order_user = "This is the value"
        expected_result = {'variable': 'value'}
        self.assertNotEqual(ActionParameterLoader._associate_order_params_to_values(order_user, order_brain),
                             expected_result)

        # Fail
        order_brain = "This is the { variable}}"
        order_user = "This is the value"
        expected_result = {'variable': 'value'}
        self.assertNotEqual(ActionParameterLoader._associate_order_params_to_values(order_user, order_brain),
                             expected_result)

        ##
        # Testing the brackets position in the sentence
        ##

        # Success
        order_brain = "{{ variable }} This is the"
        order_user = "value This is the"
        expected_result = {'variable': 'value'}
        self.assertEqual(ActionParameterLoader._associate_order_params_to_values(order_user, order_brain),
                         expected_result)

        # Success
        order_brain = "This is {{ variable }} the"
        order_user = " This is value the"
        expected_result = {'variable': 'value'}
        self.assertEqual(ActionParameterLoader._associate_order_params_to_values(order_user, order_brain),
                         expected_result)

        ##
        # Testing multi variables
        ##

        # Success
        order_brain = "This is {{ variable }} the {{ variable2 }}"
        order_user = "This is value the value2"
        expected_result = {'variable': 'value',
                           'variable2': 'value2'}
        self.assertEqual(ActionParameterLoader._associate_order_params_to_values(order_user, order_brain),
                         expected_result)

        ##
        # Testing multi words in variable
        ##

        # Success
        order_brain = "This is the {{ variable }}"
        order_user = "This is the value with multiple words"
        expected_result = {'variable': 'value with multiple words'}
        self.assertEqual(ActionParameterLoader._associate_order_params_to_values(order_user, order_brain),
                         expected_result)

        # Success
        order_brain = "This is the {{ variable }} and  {{ variable2 }}"
        order_user = "This is the value with multiple words and second value multiple"
        expected_result = {'variable': 'value with multiple words',
                           'variable2': 'second value multiple'}
        self.assertEqual(ActionParameterLoader._associate_order_params_to_values(order_user, order_brain),
                         expected_result)

        ##
        #  Specific Behaviour
        ##

        # Upper/Lower case
        order_brain = "This Is The {{ variable }}"
        order_user = "ThiS is tHe VAlue"
        expected_result = {'variable': 'VAlue'}
        self.assertEqual(ActionParameterLoader._associate_order_params_to_values(order_user, order_brain),
                         expected_result)
        # Upper/Lower case between multiple variables
        order_brain = "This Is The {{ variable }} And The {{ variable2 }}"
        order_user = "ThiS is tHe VAlue aND tHE vAlUe2"
        expected_result = {'variable': 'VAlue',
                           'variable2': 'vAlUe2'}
        self.assertEqual(ActionParameterLoader._associate_order_params_to_values(order_user, order_brain),
                         expected_result)

        # Upper/Lower case between multiple variables and at the End
        order_brain = "This Is The {{ variable }} And The {{ variable2 }} And Again"
        order_user = "ThiS is tHe VAlue aND tHE vAlUe2 and aGAIN"
        expected_result = {'variable': 'VAlue',
                           'variable2': 'vAlUe2'}
        self.assertEqual(ActionParameterLoader._associate_order_params_to_values(order_user, order_brain),
                         expected_result)

        # integers variables
        order_brain = "This Is The {{ variable }} And The {{ variable2 }}"
        order_user = "ThiS is tHe 1 aND tHE 2"
        expected_result = {'variable': '1',
                           'variable2': '2'}
        self.assertEqual(ActionParameterLoader._associate_order_params_to_values(order_user, order_brain),
                         expected_result)


if __name__ == '__main__':
    unittest.main()