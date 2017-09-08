

class Resources(object):
    """

    """
    def __init__(self, action_folder=None, stt_folder=None, tts_folder=None, wakeon_folder=None):
        self.action_folder = action_folder
        self.stt_folder = stt_folder
        self.tts_folder = tts_folder
        self.wakeon_folder = wakeon_folder

    def __str__(self):
        return str(self.serialize())

    def serialize(self):
        """
        This method allows to serialize in a proper way this object

        :return: A dict of order
        :rtype: Dict
        """

        return {
            'action_folder': self.action_folder,
            'stt_folder': self.stt_folder,
            'tts_folder': self.tts_folder,
            'wakeon_folder': self.wakeon_folder
        }

    def __eq__(self, other):
        """
        This is used to compare 2 objects
        :param other:
        :return:
        """
        return self.__dict__ == other.__dict__
