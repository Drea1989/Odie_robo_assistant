import logging

from odie.core.ActionModule import ActionModule, MissingParameterException, InvalidParameterException
from odie.actions.utils.PCA9685 import Servo

logging.basicConfig()
logger = logging.getLogger("odie")


class Servo_move(ActionModule):
    "move the servo 1 step each direction based on speach"
    # check if parameters have been provided
    def __init__(self, **kwargs):
        super(Servo_move, self).__init__(**kwargs)
        self.direction = kwargs.get('direction', None)
        servo = Servo()

        if self._is_parameters_ok():
            if self.direction == 'up':
                servo.moveServo(VStep=45)
            elif self.direction == 'down':
                servo.moveServo(VStep=-45)
            elif self.direction == 'left':
                servo.moveServo(HStep=-45)
            elif self.direction == 'right':
                servo.moveServo(HStep=45)
            else:
                logger.debug('direction not recognised')

    def _is_parameters_ok(self):
        """
        Check if received parameters are ok to perform operations in the action
        :return: true if parameters are ok, raise an exception otherwise

        .. raises:: MissingParameterException, InvalidParameterException
        """
        if self.direction is None:
            raise MissingParameterException("You must provide a direction.")
        if self.direction:
            raise InvalidParameterException("direction is not a string.")

        return True
