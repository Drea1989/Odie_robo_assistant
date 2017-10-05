import logging

from odie import CueLauncher
from odie.core.ActionModule import ActionModule

logging.basicConfig()
logger = logging.getLogger("odie")


class Mute(ActionModule):

    def __init__(self, **kwargs):
        super(Mute, self).__init__(**kwargs)

        self.status = kwargs.get('status', None)

        # check if parameters have been provided
        if self._is_parameters_ok():
            cue_order = CueLauncher.get_order_instance()
            if cue_order is not None:
                cue_order.set_mute_status(self.status)

    def _is_parameters_ok(self):
        """
        Check if received parameters are ok to perform operations in the action
        :return: true if parameters are ok, raise an exception otherwise

        .. raises:: MissingParameterException
        """
        if self.status is None:
            logger.debug("[Mute] You must specify a status with a boolean")
            return False
        return True
