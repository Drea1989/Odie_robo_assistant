import unittest
import os

from odie.core.Utils.PostgreManager import PostgresManager
from odie.core.ConfigurationManager import SettingLoader

class TestPostgreManager(unittest.TestCase):
    """
    Class to test PostgreManager
    """

    def setUp(self):
        pass

    def test_get_connection(self):
        settings_loader = SettingLoader()
        pg = settings_loader.settings.postgres
        #self.assertIsInstance(PostgresManager.get_connection(pg.host,pg.database,pg.user,pg.password))

    def test_create_engine(self):
        """
        Test to create sqlalchemy engine.
        """
        settings_loader = SettingLoader()
        pg = settings_loader.settings.postgres
        #self.assertIsInstance(PostgresManager.create_engine(pg.host,pg.database,pg.user,pg.password))

if __name__ == '__main__':
    unittest.main()
