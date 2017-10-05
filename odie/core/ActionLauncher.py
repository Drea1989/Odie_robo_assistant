import logging
import six
import jinja2

from odie.core.Utils.Utils import Utils
from odie.core.ConfigurationManager.SettingLoader import SettingLoader
from odie.core.ActionExceptions import ActionExceptions
from odie.core.Recordatio import Recordatio

logging.basicConfig()
logger = logging.getLogger("odie")


class ActionParameterNotAvailable(Exception):
    pass


class ActionLauncher:

    def __init__(self):
        pass

    @classmethod
    def launch_action(cls, action):
        """
        Start a action plugin
        :param action: action object
        :type action: action
        :return:
        """
        logger.debug("Run action: \"%s\"" % (action.__str__()))
        settings = cls.load_settings()
        action_folder = None
        if settings.resources:
            action_folder = settings.resources.action_folder

        return Utils.get_dynamic_class_instantiation(package_name="actions",
                                                     module_name=action.name,
                                                     parameters=action.parameters,
                                                     resources_dir=action_folder)

    @classmethod
    def start_action(cls, action, parameters_dict=None):
        """
        Execute each action from the received action_list.
        Replace parameter if exist in the received dict of parameters_dict
        :param action: action object to run
        :param parameters_dict: dict of parameter to load in each action if expecting a parameter
        :return: List of the instantiated actions (no errors detected)
        """
        if action.parameters is not None:
            try:
                action.parameters = cls._replace_brackets_by_loaded_parameter(action.parameters, parameters_dict)
            except ActionParameterNotAvailable:
                Utils.print_danger("Missing parameter in action %s. Execution skipped" % action.name)
                return None
        try:
            instantiated_action = ActionLauncher.launch_neuron(action)
        except ActionExceptions as e:
            Utils.print_danger("ERROR: Fail to execute action '%s'. "
                               '%s' ". -> Execution skipped" % (action.name, e.message))
            return None
        return instantiated_action

    @classmethod
    def _replace_brackets_by_loaded_parameter(cls, action_parameters, loaded_parameters):
        """
        Receive a value (which can be a str or dict or list) and instantiate value in double brace bracket
        by the value specified in the loaded_parameters dict.
        This method will call itself until all values has been instantiated
        :param action_parameters: value to instantiate. Str or dict or list
        :param loaded_parameters: dict of parameters
        """
        logger.debug("[ActionLauncher] replacing brackets from %s, using %s" % (action_parameters, loaded_parameters))
        # add variables from the short term memory to the list of loaded parameters that can be used in a template
        # the final dict is added into a key "odie_memory" to not override existing keys loaded form the order
        memory_dict = dict()
        memory_dict["odie_memory"] = Recordatio.get_memory()
        if loaded_parameters is None:
            loaded_parameters = dict()  # instantiate an empty dict in order to be able to add memory in it
        loaded_parameters.update(memory_dict)
        if isinstance(action_parameters, str) or isinstance(action_parameters, six.text_type):
            # replace bracket parameter only if the str contains brackets
            if Utils.is_containing_bracket(action_parameters):
                # check that the parameter to replace is available in the loaded_parameters dict
                if cls._action_parameters_are_available_in_loaded_parameters(action_parameters, loaded_parameters):
                    # add parameters from global variable into the final loaded parameter dict
                    settings = cls.load_settings()
                    loaded_parameters.update(settings.variables)
                    action_parameters = jinja2.Template(action_parameters).render(loaded_parameters)
                    action_parameters = Utils.encode_text_utf8(action_parameters)
                    return str(action_parameters)
                else:
                    raise ActionParameterNotAvailable
            return action_parameters

        if isinstance(action_parameters, dict):
            returned_dict = dict()
            for key, value in action_parameters.items():
                if key in "say_template" or key in "file_template" or key in "odie_memory" or key in "from_answer_link":  # keys reserved for the TTS.
                    returned_dict[key] = value
                else:
                    returned_dict[key] = cls._replace_brackets_by_loaded_parameter(value, loaded_parameters)
            return returned_dict

        if isinstance(action_parameters, list):
            returned_list = list()
            for el in action_parameters:
                templated_value = cls._replace_brackets_by_loaded_parameter(el, loaded_parameters)
                returned_list.append(templated_value)
            return returned_list
        # in all other case (boolean or int for example) we return the value as it
        return action_parameters

    @staticmethod
    def _action_parameters_are_available_in_loaded_parameters(string_parameters, loaded_parameters):
        """
        Check that all parameters in brackets are available in the loaded_parameters dict

        E.g:
        string_parameters = "this is a {{ parameter1 }}"

        Will return true if the loaded_parameters looks like the following
        loaded_parameters { "parameter1": "a value"}

        :param string_parameters: The string that contains one or more parameters in brace brackets
        :param loaded_parameters: Dict of parameter
        :return: True if all parameters in brackets have an existing key in loaded_parameters dict
        """
        list_parameters_with_brackets = Utils.find_all_matching_brackets(string_parameters)
        # remove brackets to keep only the parameter name
        for parameter_with_brackets in list_parameters_with_brackets:
            parameter = Utils.remove_spaces_in_brackets(parameter_with_brackets)
            parameter = parameter.replace("{{", "").replace("}}", "")
            if loaded_parameters is None or parameter not in loaded_parameters:
                Utils.print_danger("The parameter %s is not available in the order" % str(parameter))
                return False
        return True

    @staticmethod
    def load_settings():
        """
        Return loaded kalliope settings
        :return: setting object
        """
        sl = SettingLoader()
        return sl.settings
