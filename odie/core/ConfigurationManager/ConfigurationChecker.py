import re
import os
import imp

from odie.core.Utils.Utils import ModuleNotFoundError
from odie.core.ConfigurationManager.SettingLoader import SettingLoader

class InvalidNeuronName(Exception):
    """
    The name of the neuron is not correct. It should only contains alphanumerics at the beginning and the end of
    its name. It can also contains dash in beetween alphanumerics.
    """
    pass


class NoNeuronName(Exception):
    """
    A neuron needs a name
    """
    pass


class NoNeuronActions(Exception):
    """
    A neuron must contains at least one action

    .. seealso:: Neuron, Action
    """
    pass


class NoNeuronCues(Exception):
    """
    A neuron must contains at least an Event or an Order

    .. seealso:: Event, Order
    """
    pass


class NoValidCue(Exception):
    """
    A neuron must contains at least a valid Event or an Order

    .. seealso:: Event, Order
    """

    pass


class NoEventPeriod(Exception):
    """
    An Event must contains a period corresponding to its execution

    .. seealso:: Event
    """
    pass


class MultipleSameNeuronName(Exception):
    """
    A neuron name must be unique
    """
    pass


class NoValidOrder(Exception):
    pass


class ConfigurationChecker:
    """
    This Class provides all method to Check the configuration files are properly set up.
    """

    def __init__(self):
        pass

    @staticmethod
    def check_neuron_dict(neuron_dict):
        """
        Return True if the provided dict is well corresponding to a Neuron

        :param neuron_dict: The neuron Dictionary
        :type neuron_dict: Dict
        :return: True if neuron are ok
        :rtype: Boolean

        :Example:

            ConfigurationChecker().check_neuron_dict(neurons_dict):

        .. seealso:: Neuron
        .. raises:: NoNeuronName, InvalidNeuronName, NoNeuronActions, NoNeuronCues
        .. warnings:: Static and Public
        """

        if 'name' not in neuron_dict:
            raise NoNeuronName("The Neuron does not have a name: %s" % neuron_dict)

        # check that the name is conform
        # Regex for [a - zA - Z0 - 9\-] with dashes allowed in between but not at the start or end
        pattern = r'(?=[a-zA-Z0-9\-]{4,100}$)^[a-zA-Z0-9]+(\-[a-zA-Z0-9]+)*$'
        prog = re.compile(pattern)
        result = prog.match(neuron_dict["name"])
        if result is None:
            raise InvalidNeuronName("Error with neuron name \"%s\".Valid syntax: [a - zA - Z0 - 9\-] with dashes "
                                    "allowed in between but not at the start or end" % neuron_dict["name"])

        if 'actions' not in neuron_dict:
            raise NoNeuronActions("The Neuron does not have actions: %s" % neuron_dict)

        if 'cues' not in neuron_dict:
            raise NoNeuronCues("The Neuron does not have cues: %s" % neuron_dict)

        return True

    @staticmethod
    def check_action_dict(action_dict):
        """
        Check received action dict is valid:

        :param action_dict: The action Dictionary
        :type action_dict: Dict
        :return: True if action is ok
        :rtype: Boolean

        :Example:

            ConfigurationChecker().check_action_dict(actions_dict):

        .. seealso:: Neuron
        .. raises:: ModuleNotFoundError
        .. warnings:: Static and Public
        """

        def check_action_exist(action_module_name):
            """
            Return True if the action_name python Class exist in actions package
            :param action_module_name: Name of the action module to check
            :type action_module_name: str
            :return:
            """
            sl = SettingLoader()
            settings = sl.settings
            #composite actions
            if '.' in action_module_name:
                composite_action_module = action_module_name.strip().split(".")
                package_name = "odie.actions" + "." + composite_action_module[0].lower() + "." + composite_action_module[0].lower()
            else:
                package_name = "odie.actions" + "." + action_module_name.lower() + "." + action_module_name.lower()

            if settings.resources is not None:
                action_resource_path = settings.resources.action_folder + \
                                       os.sep + action_module_name.lower() + os.sep + \
                                       action_module_name.lower()+".py"
                if os.path.exists(action_resource_path):
                    imp.load_source(action_module_name.capitalize(), action_resource_path)
                    package_name = action_module_name.capitalize()

            try:
                if composite_action_module:
                    mod = __import__(package_name, fromlist=[composite_action_module[1].capitalize()])
                else:
                    mod = __import__(package_name, fromlist=[action_module_name.capitalize()])
                getattr(mod, action_module_name.capitalize())
            except AttributeError:
                raise ModuleNotFoundError("[AttributeError] The module %s does not exist in the package %s " % (action_module_name.capitalize(),
                                                                                                                package_name))
            except ImportError:
                raise ModuleNotFoundError("[ImportError] The module %s does not exist in the package %s " % (action_module_name.capitalize(),
                                                                                                             package_name))
            return True

        if isinstance(action_dict, dict):
            for action_name in action_dict:
                check_action_exist(action_name)
        else:
            check_action_exist(action_dict)
        return True

    @staticmethod
    def check_cue_dict(cue_dict):
        """
        Check received cue dictionary is valid:

        :param cue_dict: The cue Dictionary
        :type cue_dict: Dict
        :return: True if cue are ok
        :rtype: Boolean

        :Example:

            ConfigurationChecker().check_cue_dict(cue_dict):

        .. seealso:: Order, Event
        .. raises:: NoValidCue
        .. warnings:: Static and Public
        """

        if ('event' not in cue_dict) and ('order' not in cue_dict):
            raise NoValidCue("The cue is not an event or an order %s" % cue_dict)
        return True

    @staticmethod
    def check_event_dict(event_dict):
        """
        Check received event dictionary is valid:

        :param event_dict: The event Dictionary
        :type event_dict: Dict
        :return: True if event are ok
        :rtype: Boolean

        :Example:

            ConfigurationChecker().check_event_dict(event_dict):

        .. seealso::  Event
        .. raises:: NoEventPeriod
        .. warnings:: Static and Public
        """
        def get_key(key_name):
            try:
                return event_dict[key_name]
            except KeyError:
                return None

        if event_dict is None or event_dict == "":
            raise NoEventPeriod("Event must contain at least one of those elements: "
                                "year, month, day, week, day_of_week, hour, minute, second")

        # check content as at least on key
        year = get_key("year")
        month = get_key("month")
        day = get_key("day")
        week = get_key("week")
        day_of_week = get_key("day_of_week")
        hour = get_key("hour")
        minute = get_key("minute")
        second = get_key("second")

        list_to_check = [year, month, day, week, day_of_week, hour, minute, second]
        number_of_none_object = list_to_check.count(None)
        list_size = len(list_to_check)
        if number_of_none_object >= list_size:
            raise NoEventPeriod("Event must contain at least one of those elements: "
                                "year, month, day, week, day_of_week, hour, minute, second")

        return True

    @staticmethod
    def check_order_dict(order_dict):
        """
        Check received order dictionary is valid:

        :param order_dict: The Order Dict
        :type order_dict: Dict
        :return: True if event are ok
        :rtype: Boolean

        :Example:

            ConfigurationChecker().check_order_dict(order_dict):

        .. seealso::  Order
        .. warnings:: Static and Public
        """
        if order_dict is None or order_dict == "":
            raise NoValidOrder("An order cannot be null or empty")

        return True

    @staticmethod
    def check_neurons(neurons_list):
        """
        Check the neuron list is ok:
                - No double same name

        :param neurons_list: The Neuron List
        :type neurons_list: List
        :return: list of Neuron
        :rtype: List

        :Example:

            ConfigurationChecker().check_neurons(order_dict):

        .. seealso::  Neuron
        .. raises:: MultipleSameNeuronName
        .. warnings:: Static and Public
        """

        seen = set()
        for neuron in neurons_list:
            # convert ascii to UTF-8
            neuron_name = neuron.name.encode('utf-8')
            if neuron_name in seen:
                raise MultipleSameNeuronName("Multiple neuron found with the same name: %s" % neuron_name)
            seen.add(neuron_name)

        return True
