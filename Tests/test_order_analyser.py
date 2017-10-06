import unittest


from odie.core.Models import Brain
from odie.core.Models import Action
from odie.core.Models import Neuron
from odie.core.Models.Cue import Cue
from odie.core.Models.MatchedNeuron import MatchedNeuron
from odie.core.OrderAnalyser import OrderAnalyser


class TestOrderAnalyser(unittest.TestCase):

    """Test case for the OrderAnalyser Class"""

    def setUp(self):
        pass

    def test_get_matching_neuron(self):
        # Init
        action1 = Action(name='actione1', parameters={'var1': 'val1'})
        action2 = Action(name='actione2', parameters={'var2': 'val2'})
        action3 = Action(name='actione3', parameters={'var3': 'val3'})
        action4 = Action(name='actione4', parameters={'var4': 'val4'})

        cue1 = Cue(name="order", parameters="this is the sentence")
        cue2 = Cue(name="order", parameters="this is the second sentence")
        cue3 = Cue(name="order", parameters="that is part of the third sentence")

        neuron1 = Neuron(name="Neuron1", actions=[action1, action2], cues=[cue1])
        neuron2 = Neuron(name="Neuron2", actions=[action3, action4], cues=[cue2])
        neuron3 = Neuron(name="Neuron3", actions=[action2, action4], cues=[cue3])

        all_neuron_list = [neuron1,
                           neuron2,
                           neuron3]

        br = Brain(neurons=all_neuron_list)

        # TEST1: should return neuron1
        spoken_order = "this is the sentence"

        # Create the matched neuron
        matched_neuron_1 = MatchedNeuron(matched_neuron=neuron1,
                                         matched_order=spoken_order,
                                         user_order=spoken_order)

        matched_neurons = OrderAnalyser.get_matching_neuron(order=spoken_order, brain=br)
        self.assertEqual(len(matched_neurons), 1)
        self.assertTrue(matched_neuron_1 in matched_neurons)

        # TEST2: should return neuron1 and 2
        spoken_order = "this is the second sentence"
        matched_neurons = OrderAnalyser.get_matching_neuron(order=spoken_order, brain=br)
        self.assertEqual(len(matched_neurons), 2)
        self.assertTrue(neuron1, neuron2 in matched_neurons)

        # TEST3: should empty
        spoken_order = "not a valid order"
        matched_neurons = OrderAnalyser.get_matching_neuron(order=spoken_order, brain=br)
        self.assertFalse(matched_neurons)

    def test_spelt_order_match_brain_order_via_table(self):
        order_to_test = "this is the order"
        sentence_to_test = "this is the order"

        # Success
        self.assertTrue(OrderAnalyser.spelt_order_match_brain_order_via_table(order_to_test, sentence_to_test))

        # Failure
        sentence_to_test = "unexpected sentence"
        self.assertFalse(OrderAnalyser.spelt_order_match_brain_order_via_table(order_to_test, sentence_to_test))

        # Upper/lower cases
        sentence_to_test = "THIS is THE order"
        self.assertTrue(OrderAnalyser.spelt_order_match_brain_order_via_table(order_to_test, sentence_to_test))

    def test_get_split_order_without_bracket(self):
        # Success
        order_to_test = "this is the order"
        expected_result = ["this", "is", "the", "order"]
        self.assertEqual(OrderAnalyser._get_split_order_without_bracket(order_to_test), expected_result,
                         "No brackets Fails to return the expected list")

        order_to_test = "this is the {{ order }}"
        expected_result = ["this", "is", "the"]
        self.assertEqual(OrderAnalyser._get_split_order_without_bracket(order_to_test), expected_result,
                         "With spaced brackets Fails to return the expected list")

        order_to_test = "this is the {{order }}"    # left bracket without space
        expected_result = ["this", "is", "the"]
        self.assertEqual(OrderAnalyser._get_split_order_without_bracket(order_to_test), expected_result,
                         "Left brackets Fails to return the expected list")

        order_to_test = "this is the {{ order}}"    # right bracket without space
        expected_result = ["this", "is", "the"]
        self.assertEqual(OrderAnalyser._get_split_order_without_bracket(order_to_test), expected_result,
                         "Right brackets Fails to return the expected list")

        order_to_test = "this is the {{order}}"  # bracket without space
        expected_result = ["this", "is", "the"]
        self.assertEqual(OrderAnalyser._get_split_order_without_bracket(order_to_test), expected_result,
                         "No space brackets Fails to return the expected list")

    def test_counter_subset(self):
        list1 = ("word1", "word2")
        list2 = ("word3", "word4")
        list3 = ("word1", "word2", "word3", "word4")

        self.assertFalse(OrderAnalyser._counter_subset(list1, list2))
        self.assertTrue(OrderAnalyser._counter_subset(list1, list3))
        self.assertTrue(OrderAnalyser._counter_subset(list2, list3))


if __name__ == '__main__':
    unittest.main()
