import logging

from odie.core import Utils

logging.basicConfig()
logger = logging.getLogger("odie")


class WakeonLauncher(object):
    def __init__(self):
        pass

    @staticmethod
    def get_wakeon(settings, callback):
        """
        Start a wakeon module
        :param wakeon: wakeon object to instantiate
        :type wakeon: Wakeon
        :param callback: Callback function to call when the wakeon catch the hot word
        :return: The instance of Wakeon 
        :rtype: Wakeon
        """
        wakeon_instance = None
        for wakeon in settings.wakeons:
            if wakeon.name == settings.default_wakeon_name:
                # add the callback method to parameters
                wakeon.parameters["callback"] = callback
                logger.debug(
                    "WakeonLauncher: Start wakeon %s with parameters: %s" % (wakeon.name, wakeon.parameters))
                wakeon_instance = Utils.get_dynamic_class_instantiation(package_name="wakeon",
                                                                         module_name=wakeon.name,
                                                                         parameters=wakeon.parameters)
                break
        return wakeon_instance