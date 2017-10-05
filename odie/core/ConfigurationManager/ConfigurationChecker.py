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
            # composite actions
            composite_action_module = []
            if '.' in action_module_name:
                composite_action_module = action_module_name.strip().split(".")
                package_name = "odie.actions" + "." + composite_action_module[0].lower() + "." + composite_action_module[1].lower()
                action_module_name = composite_action_module[1]
            else:
                package_name = "odie.actions" + "." + action_module_name.lower() + "." + action_module_name.lower()

            if settings.resources.action_folder is not None:
                action_resource_path = settings.resources.action_folder + \
                                       os.sep + action_module_name.lower() + os.sep + \
                                       action_module_name.lower()+".py"
                if os.path.exists(action_resource_path):
                    imp.load_source(action_module_name.capitalize(), action_resource_path)
                    package_name = action_module_name.capitalize()

            try:
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

        def check_cue_exist(cue_name):
            """
            Return True if the cue_name python Class exist in cues package
            :param cue_name: Name of the neuron module to check
            :type cue_name: str
            :return:
            """
            sl = SettingLoader()
            settings = sl.settings
            package_name = "odie.cues" + "." + cue_name.lower() + "." + cue_name.lower()
            if settings.resources.cue_folder is not None:
                neuron_resource_path = settings.resources.neuron_folder + \
                                       os.sep + cue_name.lower() + os.sep + \
                                       cue_name.lower() + ".py"
                if os.path.exists(neuron_resource_path):
                    imp.load_source(cue_name.capitalize(), neuron_resource_path)
                    package_name = cue_name.capitalize()

            try:
                mod = __import__(package_name, fromlist=[cue_name.capitalize()])
                getattr(mod, cue_name.capitalize())
            except AttributeError:
                raise ModuleNotFoundError(
                    "[AttributeError] The module %s does not exist in the package %s " % (cue_name.capitalize(),
                                                                                          package_name))
            except ImportError:
                raise ModuleNotFoundError(
                    "[ImportError] The module %s does not exist in the package %s " % (cue_name.capitalize(),
                                                                                       package_name))
            return True

        if isinstance(cue_dict, dict):
            for cue_name in cue_dict:
                check_cue_exist(cue_name)
        else:
            check_cue_exist(cue_dict)
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
    def check_platform():
        """
        Check running on RPI:
        :return: True if is running on Pi
        :rtype: Boolean

        :Example:
            ConfigurationChecker().check_platform():
        """
        import platform

        PLATFORM = platform.system().lower()

        DEBIAN = 'debian'
        IS_LINUX = (PLATFORM == 'linux')
        RASPBERRY_PI = 'raspberry-pi'

        if IS_LINUX:
            PLATFORM = platform.linux_distribution()[0].lower()
            if PLATFORM == DEBIAN:
                try:
                    with open('/proc/cpuinfo') as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith('Hardware') and line.endswith('BCM2708'):
                                PLATFORM = RASPBERRY_PI
                                return True
                except:
                    pass

        return False

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
