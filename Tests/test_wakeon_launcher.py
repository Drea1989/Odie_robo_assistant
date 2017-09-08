import unittest
import mock

from odie.core.Models.Settings import Settings
from odie.core.WakeonLauncher import WakeonLauncher

from odie.core.Models.Wakeon import Wakeon


class TestWakeonLauncher(unittest.TestCase):
    """
    Class to test Launchers Classes (WakeonLauncher) and methods
    """

    def setUp(self):
        pass

    ####
    # Wakeon Launcher
    def test_get_wakeon(self):
        """
        Test the Wakeon Launcher trying to run the wakeon
        """
        wakeon1 = Wakeon("Wakeon", {})
        wakeon2 = Wakeon("Wakeon2", {'pmdl_file': "wakeon/snowboy/resources/odie-EN-3samples.pmdl"})
        settings = Settings()
        settings.wakeons = [wakeon1, wakeon2]
        with mock.patch("odie.core.Utils.get_dynamic_class_instantiation") as mock_get_class_instantiation:
            # Get the wakeon 1
            settings.default_wakeon_name = "Wakeon"
            WakeonLauncher.get_wakeon(settings=settings,
                                        callback=None)

            mock_get_class_instantiation.assert_called_once_with(package_name="wakeon",
                                                                 module_name=wakeon1.name,
                                                                 parameters=wakeon1.parameters)
            mock_get_class_instantiation.reset_mock()

            # Get the wakeon 2
            settings.default_wakeon_name = "Wakeon2"
            WakeonLauncher.get_wakeon(settings=settings,
                                        callback=None)

            mock_get_class_instantiation.assert_called_once_with(package_name="wakeon",
                                                                 module_name=wakeon2.name,
                                                                 parameters=wakeon2.parameters)
            mock_get_class_instantiation.reset_mock()