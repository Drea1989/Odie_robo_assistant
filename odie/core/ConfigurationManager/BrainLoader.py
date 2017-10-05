import inspect
import logging
import os
from six import with_metaclass
import six

from odie.core.Models.Cue import Cue
from .YAMLLoader import YAMLLoader
from odie.core.Utils import Utils
from odie.core.ConfigurationManager import SettingLoader
from odie.core.ConfigurationManager.ConfigurationChecker import ConfigurationChecker
from odie.core.Models import Singleton
from odie.core.Models.Brain import Brain
from odie.core.Models.Action import Action
from odie.core.Models.Neuron import Neuron

logging.basicConfig()
logger = logging.getLogger("odie")

FILE_NAME = "brain.yml"


class BrainNotFound(Exception):
    pass


class BrainLoader(with_metaclass(Singleton, object)):
    """
    This Class is used to get the brain YAML and the Brain as an object
    """

    def __init__(self, file_path=None):
        sl = SettingLoader()
        self.settings = sl.settings

        self.file_path = file_path
        if self.file_path is None:  # we don't provide a file path, so search for the default one
            self.file_path = Utils.get_real_file_path(FILE_NAME)
        else:
            self.file_path = Utils.get_real_file_path(file_path)
        # if the returned file path is none, the file doesn't exist
        if self.file_path is None:
            raise BrainNotFound("brain file not found")
        self.yaml_config = self.get_yaml_config()
        self.brain = self.get_brain()

    def get_yaml_config(self):
        """
        Class Methods which loads default or the provided YAML file and return it as a String
        :return: The loaded brain YAML
        :rtype: String

        :Example:
            brain_yaml = BrainLoader.get_yaml_config(/var/tmp/brain.yml)

        .. warnings:: Class Method
        """
        if self.file_path is None:
            brain_file_path = self._get_root_brain_path()
        else:
            brain_file_path = self.file_path
        return YAMLLoader.get_config(brain_file_path)

    def get_brain(self):
        """
        Class Methods which loads default or the provided YAML file and return a Brain
        :return: The loaded Brain
        :rtype: Brain

        :Example:

            brain = BrainLoader.get_brain(file_path="/var/tmp/brain.yml")

        .. seealso:: Brain
        .. warnings:: Class Method
        """

        # Instantiate a brain
        brain = Brain()

        # get the brain with dict
        dict_brain = self.get_yaml_config()

        brain.brain_yaml = dict_brain
        # create list of Neuron
        neurons = list()
        for neurons_dict in dict_brain:
            if "includes" not in neurons_dict:     # we don't need to check includes as it's not a neuron
                if ConfigurationChecker().check_synape_dict(neurons_dict):
                    name = neurons_dict["name"]
                    actions = self._get_actions(neurons_dict["actions"], self.settings)
                    cues = self._get_cues(neurons_dict["cues"])
                    new_neuron = Neuron(name=name, actions=actions, cues=cues)
                    neurons.append(new_neuron)
        brain.neurons = neurons
        if self.file_path is None:
            brain.brain_file = self._get_root_brain_path()
        else:
            brain.brain_file = self.file_path
        # check that no neuron have the same name than another
        if not ConfigurationChecker().check_synapes(neurons):
            brain = None

        return brain

    @classmethod
    def _get_actions(cls, actions_dict, settings):
        """
        Get a list of Action object from a action dict

        :param actions_dict: Action name or dictionary of Action_name/Action_parameters
        :type actions_dict: String or dict
        :param settings:  The Settings with the global variables
        :return: A list of Actions
        :rtype: List

        :Example:

            actions = cls._get_actions(neurons_dict["actions"])

        .. seealso:: Action
        .. warnings:: Static and Private
        """

        actions = list()
        for action_dict in actions_dict:
            if isinstance(action_dict, dict):
                if ConfigurationChecker().check_action_dict(action_dict):
                    for action_name in action_dict:

                        name = action_name
                        parameters = action_dict[name]

                        # Update brackets with the global parameter if exist
                        parameters = cls._replace_global_variables(parameter=parameters,
                                                                   settings=settings)

                        new_action = Action(name=name, parameters=parameters)
                        actions.append(new_action)
            else:
                # the action does not have parameter
                if ConfigurationChecker().check_action_dict(action_dict):
                    new_action = Action(name=action_dict)
                    actions.append(new_action)

        return actions

    @classmethod
    def _get_cues(cls, cues_dict):
        """
        Get a list of Cue object from a cues dict

        :param cues_dict: Cue name or dictionary of Cue_name/Cue_parameters
        :type cues_dict: String or dict
        :return: A list of Event and/or Order
        :rtype: List

        :Example:

            cues = cls._get_cues(neurons_dict["cues"])

        .. seealso:: Event, Order
        .. warnings:: Class method and Private
        """
        cues = list()
        for cue_dict in cues_dict:
            if ConfigurationChecker().check_cue_dict(cue_dict):
                for cue_name in cue_dict:
                    new_cue = Cue(name=cue_name, parameters=cue_dict[cue_name])
                    cues.append(new_cue)

        return cues

    @staticmethod
    def _get_root_brain_path():
        """
        Return the full path of the default brain file

        :Example:

            brain.brain_file = cls._get_root_brain_path()

        .. raises:: IOError
        .. warnings:: Static method and Private
        """

        # get current script directory path. We are in /an/unknown/path/odie/core/ConfigurationManager
        cur_script_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        # get parent dir. Now we are in /an/unknown/path/odie
        parent_dir = os.path.normpath(cur_script_directory + os.sep + os.pardir + os.sep + os.pardir)
        brain_path = parent_dir + os.sep + "brain.yml"
        logger.debug("Real brain.yml path: %s" % brain_path)
        if os.path.isfile(brain_path):
            return brain_path
        raise IOError("Default brain.yml file not found")

    @classmethod
    def _replace_global_variables(cls, parameter, settings):
        """
        replace a parameter that contains bracket by the instantiated parameter from the var file
        This function will call itself multiple time to handle different level of parameter in a action

        :param parameter: the parameter to update. can be a dict, a list or a string
        :param settings: the settings
        :return: the parameter dict
        """
        if isinstance(parameter, str) \
                or isinstance(parameter, six.text_type) \
                or isinstance(parameter, int):
            if Utils.is_containing_bracket(parameter):
                return cls._get_global_variable(sentence=parameter, settings=settings)
        if isinstance(parameter, list):
            new_parameter_list = list()
            for el in parameter:
                new_parameter_list.append(cls._replace_global_variables(el, settings=settings))
            return new_parameter_list
        if isinstance(parameter, dict):
            for key, value in parameter.items():
                parameter[key] = cls._replace_global_variables(value, settings=settings)
        return parameter

    @staticmethod
    def _get_global_variable(sentence, settings):
        """
        Get the global variable from the sentence with brackets
        :param sentence: the sentence to check
        :return: the global variable
        """
        sentence_no_spaces = Utils.remove_spaces_in_brackets(sentence=sentence)
        list_of_bracket_params = Utils.find_all_matching_brackets(sentence=sentence_no_spaces)
        for param_with_bracket in list_of_bracket_params:
            param_no_brackets = param_with_bracket.replace("{{", "").replace("}}", "")
            if param_no_brackets in settings.variables:
                logger.debug("Replacing variable %s with  %s" % (param_with_bracket,
                                                                 settings.variables[param_no_brackets]))

                # need to check if the variable is an integer
                variable = settings.variables[param_no_brackets]
                if isinstance(variable, int):
                    variable = str(variable)
                sentence_no_spaces = sentence_no_spaces.replace(param_with_bracket,
                                                                variable)
        return sentence_no_spaces
