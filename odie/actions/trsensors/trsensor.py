#!/usr/bin/python
# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO
import time
import logging

logging.basicConfig()
logger = logging.getLogger("odie")


class TRSensor(object):
    def __init__(self):

        CS = 5
        Clock = 25
        Address = 24
        DataOut = 23
        Button = 7
        self.numSensors = 5
        self.calibratedMin = [0] * self.numSensors
        self.calibratedMax = [1023] * self.numSensors
        self.last_value = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(Clock, GPIO.OUT)
        GPIO.setup(Address, GPIO.OUT)
        GPIO.setup(CS, GPIO.OUT)
        GPIO.setup(DataOut, GPIO.IN, GPIO.PUD_UP)
        GPIO.setup(Button, GPIO.IN, GPIO.PUD_UP)

    def AnalogRead(self):
        """
        Reads the sensor values into an array. There *MUST* be space
        for as many values as there were sensors specified in the constructor.
        Example usage:
        unsigned int sensor_values[8];
        sensors.read(sensor_values);
        The values returned are a measure of the reflectance in abstract units,
        with higher values corresponding to lower reflectance (e.g. a black
        surface or a void).
        """
        value = [0]*(self.numSensors+1)
        # Read Channel0~channel6 AD value
        for j in range(0, self.numSensors+1):
            GPIO.output(self.CS, GPIO.LOW)
            for i in range(0, 4):
                # sent 4-bit Address
                if(((j) >> (3 - i)) & 0x01):
                    GPIO.output(self.Address, GPIO.HIGH)
                else:
                    GPIO.output(self.Address, GPIO.LOW)
                # read MSB 4-bit data
                value[j] <<= 1
                if(GPIO.input(self.DataOut)):
                    value[j] |= 0x01
                GPIO.output(self.Clock, GPIO.HIGH)
                GPIO.output(self.Clock, GPIO.LOW)
            for i in range(0, 6):
                # read LSB 8-bit data
                value[j] <<= 1
                if(GPIO.input(self.DataOut)):
                    value[j] |= 0x01
                GPIO.output(self.Clock, GPIO.HIGH)
                GPIO.output(self.Clock, GPIO.LOW)

            time.sleep(0.0001)
            GPIO.output(self.CS, GPIO.HIGH)
        logger.debug("reading: {}".format(value[1:]))

        return value[1:]

    def calibrate(self):
        """
        Reads the sensors 10 times and uses the results for
        calibration.  The sensor values are not returned; instead, the
        maximum and minimum values found over time are stored internally
        and used for the readCalibrated() method.
        """
        max_sensor_values = [0]*self.numSensors
        min_sensor_values = [0]*self.numSensors
        for j in range(0, 10):

            sensor_values = self.AnalogRead()

            for i in range(0, self.numSensors):

                # set the max we found THIS time
                if((j == 0) or max_sensor_values[i] < sensor_values[i]):
                    max_sensor_values[i] = sensor_values[i]

                # set the min we found THIS time
                if((j == 0) or min_sensor_values[i] > sensor_values[i]):
                    min_sensor_values[i] = sensor_values[i]

        # record the min and max calibration values
        for i in range(0, self.numSensors):
            if(min_sensor_values[i] > self.calibratedMin[i]):
                self.calibratedMin[i] = min_sensor_values[i]
            if(max_sensor_values[i] < self.calibratedMax[i]):
                self.calibratedMax[i] = max_sensor_values[i]

    def readCalibrated(self):
        """
        Returns values calibrated to a value between 0 and 1000, where
        0 corresponds to the minimum value read by calibrate() and 1000
        corresponds to the maximum value.  Calibration values are
        stored separately for each sensor, so that differences in the
        sensors are accounted for automatically.
        """
        value = 0
        # read the needed values
        sensor_values = self.AnalogRead()

        for i in range(0, self.numSensors):

            denominator = self.calibratedMax[i] - self.calibratedMin[i]

            if(denominator != 0):
                value = (sensor_values[i] - self.calibratedMin[i]) * 1000 / denominator

            if(value < 0):
                value = 0
            elif(value > 1000):
                value = 1000

            sensor_values[i] = value

        logger.debug("readCalibrated: {}".format(sensor_values))
        return sensor_values
