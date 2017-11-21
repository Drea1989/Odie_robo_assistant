import logging
import time

from odie.core.ActionModule import ActionModule, MissingParameterException
from odie.actions.utils.AlphaBot import AlphaBot

logging.basicConfig()
logger = logging.getLogger("odie")


class Rover_set(ActionModule):
    def __init__(self, **kwargs):
        super(Rover_set, self).__init__(**kwargs)

        self.direction = kwargs.get('direction', None)

        if self._is_parameters_ok():
            AB = AlphaBot()

            try:
                if self.direction == "stop":
                    AB.stop()
                elif self.direction == "forward":
                    AB.forward()
                    time.sleep(.5)
                    AB.stop()
                elif self.direction == "backward":
                    AB.backward()
                    time.sleep(.5)
                    AB.stop()
                elif self.direction == "turnleft":
                    AB.left()
                    time.sleep(.5)
                    AB.stop()
                elif self.direction == "turnright":
                    AB.right()
                    time.sleep(.5)
                    AB.stop()
                elif self.direction == "buzzeron":
                    AB.buzz()
            except:
                AB.stop()
                logger.debug("Command error: {}".format(self.direction))

    def _is_parameters_ok(self):
        """
        Check if received parameters are ok to perform operations in the action
        :return: true if parameters are ok, raise an exception otherwise
        .. raises:: NotImplementedError
        """
        if self.direction is None:
            raise MissingParameterException("AlphaBot need a direction parameter")

        return True
