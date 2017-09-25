import logging

from odie.core.ActionModule import ActionModule
from odie.actions.alphabot import AlphaBot

logging.basicConfig()
logger = logging.getLogger("odie")


class Setrover(ActionModule):
    def __init__(self, **kwargs):
        super(Setrover, self).__init__(**kwargs)

        AB = AlphaBot()
        self.direction = kwargs.get('direction', None)

        if self._is_parameters_ok():

            try:
                if direction == "stop":
                    AB.stop()
                elif direction == "forward":
                    AB.forward()
                elif direction == "backward":
                    AB.backward()
                elif direction == "turnleft":
                    AB.left()
                elif direction == "turnright":
                    AB.right()
                elif direction == "buzzeron":
                    AB.buzz()
            except:
                AB.stop()
                logger.debug("Command error: {}".format(direction))

    def _is_parameters_ok(self):
        """
        Check if received parameters are ok to perform operations in the action
        :return: true if parameters are ok, raise an exception otherwise
        .. raises:: NotImplementedError
        """
        if self.direction is None:
            raise MissingParameterException("AlphaBot need a direction parameter")

        return True
