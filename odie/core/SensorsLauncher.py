import logging

from odie.core import Utils

logging.basicConfig()
logger = logging.getLogger("odie")


class SensorsLauncher(object):
    def __init__(self):
    """
    class for starting, terminating all sensors.
    
    """
        pass

    @staticmethod
    def get_IR(settings, callback):
        """
        Start a IR module
        :param IR: wakeon object to instantiate
        :type IR: Wakeon
        :param callback: Callback function to call when the IR catch the hot word
        :return: The instance of IR 
        :rtype: IR
        """
        #TODO: Sensor initialise 
        IR_instance = None
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