import logging
import sys
import threading
import time

from odie.core import ActionModule
from odie.core.ActionModule import MissingParameterException, InvalidParameterException

logging.basicConfig()
logger = logging.getLogger("odie")


class TimerThread(threading.Thread):
    def __init__(self, time_to_wait_seconds, callback):
        """
        A Thread that will call the given callback method after waiting time_to_wait_seconds
        :param time_to_wait_seconds: number of second to wait before call the callback method
        :param callback: callback method
        """
        threading.Thread.__init__(self)
        self.time_to_wait_seconds = time_to_wait_seconds
        self.callback = callback

    def run(self):
        # wait the amount of seconds
        logger.debug("[Neurotimer] wait %s seconds" % self.time_to_wait_seconds)
        time.sleep(self.time_to_wait_seconds)
        # then run the callback method
        self.callback()


class Neurotimer(ActionModule):
    def __init__(self, **kwargs):
        super(Neurotimer, self).__init__(**kwargs)

        # get parameters
        self.seconds = kwargs.get('seconds', None)
        self.minutes = kwargs.get('minutes', None)
        self.hours = kwargs.get('hours', None)
        self.neuron = kwargs.get('neuron', None)
        self.forwarded_parameter = kwargs.get('forwarded_parameters', None)

        # do some check
        if self._is_parameters_ok():
            # make the sum of all time parameter in seconds
            retarding_time_seconds = self._get_retarding_time_seconds()

            # now wait before running the target neuron
            ds = TimerThread(time_to_wait_seconds=retarding_time_seconds, callback=self.callback_run_neuron)
            # ds.daemon = True
            ds.start()

    def _is_parameters_ok(self):
        """
        Check given action parameters are valid
        :return: True if the action has been well configured
        """

        # at least one time parameter must be set
        if self.seconds is None and self.minutes is None and self.hours is None:
            raise MissingParameterException("Neurotimer must have at least one time "
                                            "parameter: seconds, minutes, hours")

        self.seconds = self.get_integer_time_parameter(self.seconds)
        self.minutes = self.get_integer_time_parameter(self.minutes)
        self.hours = self.get_integer_time_parameter(self.hours)
        if self.neuron is None:
            raise MissingParameterException("Neurotimer must have a neuron name parameter")

        return True

    @staticmethod
    def get_integer_time_parameter(time_parameter):
        """
        Check if a given time parameter is a valid integer:
        - must be > 0
        - if type no an integer, must be convertible to integer

        :param time_parameter: string or integer
        :return: integer
        """
        if time_parameter is not None:
            if not isinstance(time_parameter, int):
                # try to convert into integer
                try:
                    time_parameter = int(time_parameter)
                except ValueError:
                    raise InvalidParameterException("[Neurotimer] %s is not a valid integer" % time_parameter)
            # check if positive
            if time_parameter < 0:
                raise InvalidParameterException("[Neurotimer] %s must be > 0" % time_parameter)

        return time_parameter

    def _get_retarding_time_seconds(self):
        """
        Return the sum of given time parameters
        seconds + minutes + hours
        :return: integer, number of total seconds
        """
        returned_time = 0

        if self.seconds is not None:
            returned_time += self.seconds
        if self.minutes is not None:
            returned_time += self.minutes * 60
        if self.hours is not None:
            returned_time += self.hours * 3600

        logger.debug("[Neurotimer] get_retarding_time_seconds: %s" % returned_time)
        return returned_time

    def callback_run_neuron(self):
        """
        Callback method which will be started by the timer thread once the time is over
        :return:
        """
        logger.debug("[Neurotimer] waiting time is over, start the neuron %s" % self.neuron)
        # trick to remove unicode problem when loading jinja template with non ascii char
        if sys.version_info[0] == 2:
            reload(sys)
            sys.setdefaultencoding('utf-8')

        self.run_neuron_by_name(neuron_name=self.neuron,
                                high_priority=False,
                                overriding_parameter_dict=self.forwarded_parameter)
