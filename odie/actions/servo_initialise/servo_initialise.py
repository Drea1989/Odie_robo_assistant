import logging

from odie.core.ActionModule import ActionModule
from odie.actions.utils.PCA9685 import Servo

logging.basicConfig()
logger = logging.getLogger("odie")


class Servo_initialise(ActionModule):
    """
    this set the servo to the centred position
    """
    def __init__(self, **kwargs):
        super(Servo_initialise, self).__init__(**kwargs)
        servo = Servo()
        # Set the Horizontal servo parameters
        servo.set_servo_pulse(0, 410)
        # Set the vertical servo parameters
        servo.set_servo_pulse(1, 410)
