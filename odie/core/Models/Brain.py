
class Brain:
    """
    This Class is a Singleton Representing the Brain.yml file with neuron
    .. note:: the is_loaded Boolean is True when the Brain has been properly loaded.
    """

    def __init__(self, neurons=None, brain_file=None, brain_yaml=None):
        self.neurons = neurons
        self.brain_file = brain_file
        self.brain_yaml = brain_yaml

    def get_neuron_by_name(self, neuron_name):
        """
        Get the neuron, using its neuron name, from the neuron list
        :param neuron_name: the name of the neuron to get
        :type neuron_name: str
        :return: The Neuron corresponding to the name
        :rtype: Neuron
        """
        neuron_launched = None
        for neuron in self.neurons:
            if neuron.name == neuron_name:
                neuron_launched = neuron
                # we found the neuron, we don't need to check the rest of the list
                break
        return neuron_launched

    def __eq__(self, other):
        """
        This is used to compare 2 objects
        :param other:
        :return:
        """
        return self.__dict__ == other.__dict__
