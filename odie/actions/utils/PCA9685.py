# !/usr/bin/python
from __future__ import division

try:
    # only import if we are on a Rpi
    import Adafruit_PCA9685
except:
    pass
import logging

logging.basicConfig()
logger = logging.getLogger("odie")

# ============================================================================
# Raspi PCA9685 16-Channel PWM Servo Driver
# ============================================================================


class Servo(object):
    """
    class to move the servo up/down and left/right
    """
    def __init__(self):
        # Initialise the PCA9685 using the default address (0x40).
        self.pwm = Adafruit_PCA9685.PCA9685()
        self.max = 600
        self.min = 150
        # Alternatively specify a different address and/or bus:
        # pwm = Adafruit_PCA9685.PCA9685(address=0x41, busnum=2)

        self.pulse_length = 1000000    # 1,000,000 us per second
        self.pulse_length //= 60       # 60 Hz
        logger.debug('{0}us per period'.format(self.pulse_length))
        self.pulse_length //= 4096     # 12 bits of resolution
        logger.debug('{0}us per bit'.format(self.pulse_length))
        # Set frequency to 60hz, good for servos.
        self.pwm.set_pwm_freq(60)

    def _servo_degrees_to_us(self, angle):
        """Converts degrees into a servo pulse time in microseconds
        :param angle: Angle in degrees from -90 to 90
        """

        self._check_range(angle, -90, 90)

        angle += 90
        servo_range = self.max - self.min
        us = (servo_range / 180.0) * angle
        return self.min + int(us)

    def _check_range(self, value, value_min, value_max):
        """Check the type and bounds check an expected int value."""

        if value < value_min or value > value_max:
            raise ValueError("Value {value} should be between {min} and {max}".format(
                value=value,
                min=value_min,
                max=value_max))

    # Helper function to make setting a servo pulse width simpler.
    def set_servo_pulse(self, channel, pulse):
        pulse = self.validate_pulse(channel, pulse)
        self.pwm.set_pwm(channel, 0, pulse)

    def validate_pulse(self, channel, pulse):
        return max(self.min, min(self.max, pulse))

    def moveServo(self, HStep=None, VStep=None):
        if HStep is not None:
            self.set_servo_pulse(0, self._servo_degrees_to_us(HStep))
        elif VStep is not None:
            self.set_servo_pulse(1, self._servo_degrees_to_us(VStep))
        else:
            logger.debug("[SERVO] error in input values")
