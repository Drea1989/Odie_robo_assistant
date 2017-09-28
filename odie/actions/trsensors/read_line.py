
from odie.actions.trsensors.trsensor import TRSensor
from odie.core.ActionModule import ActionModule
import logging

logging.basicConfig()
logger = logging.getLogger("odie")


class Read_line(ActionModule):
    def __init__(self, **kwargs):
        super(Read_line, self).__init__(**kwargs)
        """
        Operates the same as read calibrated, but also returns an
        estimated position of the robot with respect to a line. The
        estimate is made using a weighted average of the sensor indices
        multiplied by 1000, so that a return value of 0 indicates that
        the line is directly below sensor 0, a return value of 1000
        indicates that the line is directly below sensor 1, 2000
        indicates that it's below sensor 2000, etc.  Intermediate
        values indicate that the line is between two sensors.  The
        formula is:

           0*value0 + 1000*value1 + 2000*value2 + ...
           --------------------------------------------
                 value0  +  value1  +  value2 + ...

        By default, this function assumes a dark line (high values)
        surrounded by white (low values).  If your line is light on
        black, set the optional second argument white_line to true.  In
        this case, each sensor value will be replaced by (1000-value)
        before the averaging.
        """
        self.white_line = kwargs.get('white_line', 0)

        TR = TRSensor()
        sensor_values = TR.readCalibrated()

        avg = 0
        sum = 0
        on_line = 0
        for i in range(0, TR.numSensors):
            value = sensor_values[i]
            if(self.white_line):
                value = 1000-value
            # keep track of whether we see the line at all
            if(value > 200):
                on_line = 1

            # only average in values that are above a noise threshold
            if(value > 50):
                avg += value * (i * 1000)  # this is for the weighted total,
                sum += value                  # this is for the denominator

        if(on_line != 1):
            # If it last read to the left of center, return 0.
            if(self.last_value < (TR.numSensors - 1)*1000/2):
                logger.debug("left")
                self.last_value = 0

            # If it last read to the right of center, return the max.
            else:
                logger.debug("right")
                self.last_value = (TR.numSensors - 1)*1000
        else:
            self.last_value = avg/sum

        return self.last_value, sensor_values
