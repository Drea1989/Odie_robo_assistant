import RPi.GPIO as GPIO
import time
import logging
from neopixel import Adafruit_NeoPixel

from odie.core.ActionModule import ActionModule

logging.basicConfig()
logger = logging.getLogger("odie")

class AlphaBot(ActionModule):
    """
    class to control the movements of the robot
    """
    def __init__(self,ain1=12,ain2=13,ena=6,bin1=20,bin2=21,enb=26, **kwargs):
        super(AlphaBot, self).__init__(**kwargs)

        self.direction = kwargs.get('direction', None)

        self.AIN1 = ain1
        self.AIN2 = ain2
        self.BIN1 = bin1
        self.BIN2 = bin2
        self.ENA = ena
        self.ENB = enb
        self.PA  = 50
        self.PB  = 50
        self.DR = 16
        self.DL = 19
        self.BUZ = 4

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.AIN1,GPIO.OUT)
        GPIO.setup(self.AIN2,GPIO.OUT)
        GPIO.setup(self.BIN1,GPIO.OUT)
        GPIO.setup(self.BIN2,GPIO.OUT)
        GPIO.setup(self.ENA,GPIO.OUT)
        GPIO.setup(self.ENB,GPIO.OUT)
        GPIO.setup(BUZ,GPIO.OUT)
        GPIO.setup(DR,GPIO.IN,GPIO.PUD_UP)
        GPIO.setup(DL,GPIO.IN,GPIO.PUD_UP)
        self.PWMA = GPIO.PWM(self.ENA,500)
        self.PWMB = GPIO.PWM(self.ENB,500)
        self.PWMA.start(self.PA)
        self.PWMB.start(self.PB)
        self.stop()

    def forward(self):
        self.PWMA.ChangeDutyCycle(self.PA)
        self.PWMB.ChangeDutyCycle(self.PB)
        GPIO.output(self.AIN1,GPIO.LOW)
        GPIO.output(self.AIN2,GPIO.HIGH)
        GPIO.output(self.BIN1,GPIO.LOW)
        GPIO.output(self.BIN2,GPIO.HIGH)


    def stop(self):
        self.PWMA.ChangeDutyCycle(0)
        self.PWMB.ChangeDutyCycle(0)
        GPIO.output(self.AIN1,GPIO.LOW)
        GPIO.output(self.AIN2,GPIO.LOW)
        GPIO.output(self.BIN1,GPIO.LOW)
        GPIO.output(self.BIN2,GPIO.LOW)

    def backward(self):
        self.PWMA.ChangeDutyCycle(self.PA)
        self.PWMB.ChangeDutyCycle(self.PB)
        GPIO.output(self.AIN1,GPIO.HIGH)
        GPIO.output(self.AIN2,GPIO.LOW)
        GPIO.output(self.BIN1,GPIO.HIGH)
        GPIO.output(self.BIN2,GPIO.LOW)

        
    def left(self):
        self.PWMA.ChangeDutyCycle(30)
        self.PWMB.ChangeDutyCycle(30)
        GPIO.output(self.AIN1,GPIO.HIGH)
        GPIO.output(self.AIN2,GPIO.LOW)
        GPIO.output(self.BIN1,GPIO.LOW)
        GPIO.output(self.BIN2,GPIO.HIGH)


    def right(self):
        self.PWMA.ChangeDutyCycle(30)
        self.PWMB.ChangeDutyCycle(30)
        GPIO.output(self.AIN1,GPIO.LOW)
        GPIO.output(self.AIN2,GPIO.HIGH)
        GPIO.output(self.BIN1,GPIO.HIGH)
        GPIO.output(self.BIN2,GPIO.LOW)
        
    def setPWMA(self,value):
        self.PA = value
        self.PWMA.ChangeDutyCycle(self.PA)

    def setPWMB(self,value):
        self.PB = value
        self.PWMB.ChangeDutyCycle(self.PB)  
        
    def setMotor(self, left, right):
        if((right >= 0) and (right <= 100)):
            GPIO.output(self.AIN1,GPIO.HIGH)
            GPIO.output(self.AIN2,GPIO.LOW)
            self.PWMA.ChangeDutyCycle(right)
        elif((right < 0) and (right >= -100)):
            GPIO.output(self.AIN1,GPIO.LOW)
            GPIO.output(self.AIN2,GPIO.HIGH)
            self.PWMA.ChangeDutyCycle(0 - right)
        if((left >= 0) and (left <= 100)):
            GPIO.output(self.BIN1,GPIO.HIGH)
            GPIO.output(self.BIN2,GPIO.LOW)
            self.PWMB.ChangeDutyCycle(left)
        elif((left < 0) and (left >= -100)):
            GPIO.output(self.BIN1,GPIO.LOW)
            GPIO.output(self.BIN2,GPIO.HIGH)
            self.PWMB.ChangeDutyCycle(0 - left)

    def setMove(self,direction):
        if self._is_parameters_ok():
            
            try:
                if direction == "stop":
                    self.stop()
                elif direction == "forward":
                    self.forward()
                elif direction == "backward":
                    self.backward()
                elif direction == "turnleft":
                    self.left()
                elif direction == "turnright":
                    self.right()
                elif direction == "buzzeron":
                    self.buzz()
            except:
                self.stop()
                logger.debug("Command error: {}".format(direction))

    def buzz(self):
        GPIO.output(BUZ,GPIO.HIGH)
        GPIO.output(BUZ,GPIO.LOW)

    def infrared(self):
        """
        return status of the infrared sensors
        if reading is == 0 there is an obstacle nearby
        :return: left reading, right reading
        """
        return  GPIO.input(DL),GPIO.input(DR)

    def LedLights(self,LedDict):
        """
        :param:LedDict is the RGB values of the color the LED should be
        it is provided as a dictionary of LED number and a list of RGB color combination: 
        {0 : [0,255,0], 1: [255,0,0], 2:[0,0,255],3:[255,255,0]}
        """
        # LED strip configuration:
        LED_COUNT      = 4      # Number of LED pixels.
        LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
        LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
        LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
        LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

        # Create NeoPixel object with appropriate configuration.
        strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
        # Intialize the library (must be called once before other functions).
        strip.begin()
        for led in LedDict:         
            strip.setPixelColor(led,LedDict[led].values)
        strip.show()

    def _is_parameters_ok(self):
        """
        Check if received parameters are ok to perform operations in the action
        :return: true if parameters are ok, raise an exception otherwise
        .. raises:: NotImplementedError
        """
        if self.direction is None:
            raise MissingParameterException("AlphaBot need a direction parameter")

        return True