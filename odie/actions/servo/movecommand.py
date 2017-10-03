import logging

from odie.core.ActionModule import ActionModule, MissingParameterException, InvalidParameterException
from odie.actions.servo.PCA9685 import Servo

logging.basicConfig()
logger = logging.getLogger("odie")


class Movecommand(ActionModule):
    "move the servo 1 step each direction based on speach"
    # check if parameters have been provided
    def __init__(self, **kwargs):
        super(Movecommand, self).__init__(**kwargs)
        self.direction = kwargs.get('direction', None)
        self.HStep = kwargs.get('HStep', 0)
        self.VStep = kwargs.get('VStep', 0)
        servo = Servo()

        if self._is_parameters_ok():
            if self.direction == 'up':
                servo.moveServo(HStep=500)
            elif self.direction == 'down':
                servo.moveServo(HStep=-500)
            elif self.direction == 'left':
                servo.moveServo(VStep=-500)
            elif self.direction == 'right':
                servo.moveServo(VStep=500)
            elif self.HStep != 0 or self.VStep != 0:
                servo.moveServo(VStep=self.VStep, HStep=self.HStep)
            else:
                logger.debug('direction not recognised')

    def _is_parameters_ok(self):
        """
        Check if received parameters are ok to perform operations in the action
        :return: true if parameters are ok, raise an exception otherwise

        .. raises:: MissingParameterException, InvalidParameterException
        """
        if self.HStep is None and self.vStep is None and self.direction is None:
            raise MissingParameterException("You must provide a step.")
        if self.HStep or self.vStep:
            raise InvalidParameterException("Step is not a number.")
        if self.direction is None:
            raise MissingParameterException("You must provide a direction.")
        if self.direction:
            raise InvalidParameterException("direction is not a string.")

        return True
