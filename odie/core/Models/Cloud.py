

class Cloud(object):
    """
    Cloud object
    parameters can be:
    :param: model # to pass the model file
    :param: TFhost # to pass the host of tensorflow serving
    :param: TFport # to pass the port of tensorflow serving
    """
    def __init__(self, category=None, parameters=None):
        self.category = category
        self.parameters = parameters

    def __str__(self):
        return str(self.serialize())

    def serialize(self):
        """
        This method allows to serialize in a proper way this object

        :return: A dict of order
        :rtype: Dict
        """

        return {
            'category': self.category,
            'parameters': self.parameters
        }

    def __eq__(self, other):
        """
        This is used to compare 2 objects
        :param other:
        :return:
        """
        return self.__dict__ == other.__dict__
