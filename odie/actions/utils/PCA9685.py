# !/usr/bin/python

import time
import math
try:
    # only import if we are on a Rpi
    import smbus
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
    def __init__(self, address=0x40):
        self.bus = smbus.SMBus(1)
        self.address = address
        self.HPulse = 1500  # Sets the initial Pulse
        self.VPulse = 1500  # Sets the initial Pulse
        # Registers/etc.
        __SUBADR1            = 0x02
        __SUBADR2            = 0x03
        __SUBADR3            = 0x04
        __MODE1              = 0x00
        __PRESCALE           = 0xFE
        __LED0_ON_L          = 0x06
        __LED0_ON_H          = 0x07
        __LED0_OFF_L         = 0x08
        __LED0_OFF_H         = 0x09
        __ALLLED_ON_L        = 0xFA
        __ALLLED_ON_H        = 0xFB
        __ALLLED_OFF_L       = 0xFC
        __ALLLED_OFF_H       = 0xFD
        logger.debug("Reseting PCA9685")
        self.write(self.__MODE1, 0x00)

    def write(self, reg, value):
        "Writes an 8-bit value to the specified register/address"
        self.bus.write_byte_data(self.address, reg, value)
        logger.debug("I2C: Write 0x%02X to register 0x%02X" % (value, reg))

    def read(self, reg):
        "Read an unsigned byte from the I2C device"
        result = self.bus.read_byte_data(self.address, reg)
        logger.debug("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
        return result

    def setPWMFreq(self, freq):
        "Sets the PWM frequency"
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq)
        prescaleval -= 1.0
        logger.debug("Setting PWM frequency to %d Hz" % freq)
        logger.debug("Estimated pre-scale: %d" % prescaleval)
        prescale = math.floor(prescaleval + 0.5)
        logger.debug("Final pre-scale: %d" % prescale)

        oldmode = self.read(self.__MODE1)
        newmode = (oldmode & 0x7F) | 0x10        # sleep
        self.write(self.__MODE1, newmode)        # go to sleep
        self.write(self.__PRESCALE, int(math.floor(prescale)))
        self.write(self.__MODE1, oldmode)
        time.sleep(0.005)
        self.write(self.__MODE1, oldmode | 0x80)

    def setPWM(self, channel, on, off):
        "Sets a single PWM channel"
        self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
        self.write(self.__LED0_ON_H+4*channel, on >> 8)
        self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
        self.write(self.__LED0_OFF_H+4*channel, off >> 8)
        logger.debug("channel: %d  LED_ON: %d LED_OFF: %d" % (channel, on, off))

    def setServoPulse(self, channel, pulse):
        "Sets the Servo Pulse,The PWM frequency must be 50HZ"
        pulse = pulse*4096/20000        # PWM frequency is 50HZ,the period is 20000us
        self.setPWM(channel, 0, pulse)

    def moveServo(self, HStep=0, VStep=0):
        """
        this move the servo vertically and/or horizontally by a integer step
        """
        if(HStep != 0):
            self.HPulse += HStep
            if(self.HPulse >= 2500):
                self.HPulse = 2500
            if(self.HPulse <= 500):
                self.HPulse = 500
            # set channel 2, the Horizontal servo
            self.setServoPulse(0, self.HPulse)

        if(VStep != 0):
            self.VPulse += VStep
            if(self.VPulse >= 2500):
                self.VPulse = 2500
            if(self.VPulse <= 500):
                self.VPulse = 500
            # set channel 3, the vertical servo
            self.setServoPulse(1, self.VPulse)
