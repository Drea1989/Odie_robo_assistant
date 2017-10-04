

class Cloud(object):
    """
    Cloud ojbect
    """
    def __init__(self, category=None, model=None, TFhost=None, TFport=None):
        self.category = category
        self.model = model
        self.TFhost = TFhost
        self.TFport = TFport

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
            'model': self.model,
            'tfhost':  self.TFhost,
            'tfport':  self.TFport
        }

    def __eq__(self, other):
        """
        This is used to compare 2 objects
        :param other:
        :return:
        """
        return self.__dict__ == other.__dict__
