import logging
import os

import sys

from sqlalchemy import create_engine
import psycopg2


logging.basicConfig()
logger = logging.getLogger("odie")


class PostgresManager(object):
    """
    Class used to manage PostgreSQL
    """
    def __init__(self):
        pass

    @staticmethod
    def get_connection(host,database,user,password):
        """
        Create a connection object with PostgreSQL
        :param host: the PostgreSQL host address
        :type host: str
        :param database: the PostgreSQL database
        :type database: str
        :param user: the PostgreSQL user
        :type user: str
        :param password: the PostgreSQL password
        :type password: str
        """
        try:
            return psycopg2.connect(host,database,user,password)
        except:
            logger.error("PostgreSQL Connection failed")

    @staticmethod
    def create_engine(host='localhost',port=5432,database=None,user=None,password=None):
        """
        Create an sqlalchemy engine object
        :param host: the PostgreSQL host address
        :type host: str
        :param database: the PostgreSQL database
        :type database: str
        :param user: the PostgreSQL user
        :type user: str
        :param password: the PostgreSQL password
        :type password: str

        .. raises:: IOError
        """
        try:
            return create_engine('postgresql://'+user+':'+password+'@'+host+':'+str(port)+'/'+database)
        except:
            logger.error("PostgreSQL could not create an engine")
