class Neuron(object):
    """
    This Class is representing a Neuron with its name, and a dict of actions and a dict of cues

    .. note:: must be defined in the brain.yml
    """

    def __init__(self, name=None, actions=None, cues=None):
        self.name = name
        self.actions = actions
        self.cues = cues

    def serialize(self):
        """
        This method allows to serialize in a proper way this object

        :return: A dict of name, actions, cues
        :rtype: Dict
        """

        return {
            'name': self.name,
            'actions': [e.serialize() for e in self.actions],
            'cues': [e.serialize() for e in self.cues]
        }

    def __str__(self):
        return str(self.serialize())

    def __eq__(self, other):
        """
        This is used to compare 2 objects
        :param other:
        :return:
        """
        return self.__dict__ == other.__dict__
