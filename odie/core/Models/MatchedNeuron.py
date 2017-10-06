import copy

from odie.core.ActionParameterLoader import ActionParameterLoader


class MatchedNeuron(object):
    """
    This class represent a neuron that has matched an order send by an User.
    """

    def __init__(self, matched_neuron=None, matched_order=None, user_order=None, overriding_parameter=None):
        """
        :param matched_neuron: The neuron that has matched in the brain.
        :param matched_order: The order from the neuron that have matched.
        :param user_order: The order said by the user.
        :param overriding_parameter: If set, those parameters will over
        """

        # create a copy of the neuron. the received neuron come from the brain.
        self.neuron = matched_neuron
        # create a fifo list that contains all actions to process.
        # Create a copy to be sure when we remove a action from this list it will not be removed from the neuron's
        # action list
        self.action_fifo_list = copy.deepcopy(self.neuron.actions)
        self.matched_order = matched_order
        self.parameters = dict()
        if matched_order is not None:
            self.parameters = ActionParameterLoader.get_parameters(neuron_order=self.matched_order,
                                                                   user_order=user_order)
        if overriding_parameter is not None:
            # we suppose that we don't have any parameters.
            # We replace the current parameter object with the received one
            self.parameters.update(overriding_parameter)

        # list of Action Module
        self.action_module_list = list()

    def __str__(self):
        return str(self.serialize())

    def serialize(self):
        """
        This method allows to serialize in a proper way this object

        :return: A dict of name and parameters
        :rtype: Dict
        """
        return {
            'neuron_name': self.neuron.name,
            'matched_order': self.matched_order,
            'action_module_list': [e.serialize() for e in self.action_module_list]
        }

    def __eq__(self, other):
        """
        This is used to compare 2 objects
        :param other:
        :return:
        """
        return self.__dict__ == other.__dict__
