

class Postgres(object):
    """
    postgres ojbect
    """
    def __init__(self,host='localhost',port=5432,database=None,user=None,password=None):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password

    def __str__(self):
        return str(self.serialize())

    def serialize(self):
        """
        This method allows to serialize in a proper way this object

        :return: A dict of order
        :rtype: Dict
        """

        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password
        }

    def __eq__(self, other):
        """
        This is used to compare 2 objects
        :param other:
        :return:
        """
        return self.__dict__ == other.__dict__
