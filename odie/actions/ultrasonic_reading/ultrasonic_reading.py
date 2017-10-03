import RPi.GPIO as GPIO
import time
import logging
from odie.core.ActionModule import ActionModule

logging.basicConfig()
logger = logging.getLogger("odie")


class Ultrasonic_reading(ActionModule):

    def __init__(self, **kwargs):
        super(Ultrasonic_reading, self).__init__(**kwargs)

        TRIG = 22
        ECHO = 27
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(TRIG, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(ECHO, GPIO.IN)
        # calculating distance
        GPIO.output(TRIG, GPIO.HIGH)
        time.sleep(0.000015)
        GPIO.output(TRIG, GPIO.LOW)
        while not GPIO.input(ECHO):
            pass
        t1 = time.time()
        logger.debug("t1 is : {}".format(t1))
        while GPIO.input(ECHO):
            pass
        t2 = time.time()
        logger.debug("t2 is : {}".format(t2))
        logger.debug("readings : {}".format((t2-t1)*34000/2))
        return (t2-t1)*34000/2
