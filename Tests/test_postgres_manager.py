import unittest

from odie.postgres.PostgreManager import PostgresManager
from odie.core.ConfigurationManager import SettingLoader
from odie.core.ConfigurationManager import BrainLoader


class TestPostgreManager(unittest.TestCase):
    """
    Class to test PostgreManager
    """

    def setUp(self):
        pass

    def test_get_connection(self):
        settings_loader = SettingLoader()
        pg = settings_loader.settings.postgres
        try:
            connect = PostgresManager.get_connection(pg.host, pg.database, pg.user, pg.password)
            connect.close()
            return True
        except:
            return False

    def test_create_engine(self):
        """
        Test to create sqlalchemy engine.
        """
        settings_loader = SettingLoader()
        pg = settings_loader.settings.postgres
        try:
            engine = PostgresManager.create_engine(pg.host, pg.database, pg.user, pg.password)
            connect = engine.connect()
            connect.close()
            return True
        except:
            return False

    def test_create_table(self):
        """
        Test to create brain table.
        """
        settings_loader = SettingLoader()
        brain_loader = BrainLoader(file_path=None)
        pg = settings_loader.settings.postgres
        brain = brain_loader.brain
        try:
            Bsaved = PostgresManager.save_brain_table(pg=pg, brain=brain)
            return True
        except:
            return False

    def test_create_index(self):
        settings_loader = SettingLoader()
        pg = settings_loader.settings.postgres
        connect = PostgresManager.get_connection(pg.host, pg.database, pg.user, pg.password)
        try:
            PostgresManager.create_text_search_index(connect)
            return True
        except:
            return False

    def test_match_neuron(self):
        settings_loader = SettingLoader()
        pg = settings_loader.settings.postgres
        connect = PostgresManager.get_connection(pg.host, pg.database, pg.user, pg.password)
        try:
            match = PostgresManager.search_match_neuron(connect, 'hello')
            self.assertEqual(match, 'say-hello')
        except:
            return False


if __name__ == '__main__':
    unittest.main()
