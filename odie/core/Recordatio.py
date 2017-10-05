import logging

import jinja2
from odie.core.Utils.Utils import Utils

from odie.core.Models import Singleton
from six import with_metaclass

logging.basicConfig()
logger = logging.getLogger("odie")


class Recordatio(with_metaclass(Singleton, object)):
    """
    short-term memories of odie. Used to store object with a "key" "value"
    """
    # this dict contains the short term memory of odie.
    # all keys present in this dict has been saved from a user demand
    memory = dict()
    # this is a temp dict that allow us to store temporary parameters that as been loaded from the user order
    # if the user want to a key from this dict, the key and its value will be added o the memory dict
    temp = dict()

    def __init__(self):
        logger.debug("[Recordatio] New memory created")

    @classmethod
    def get_memory(cls):
        """
        Get the current dict of parameters saved in memory
        :return: dict memory
        """
        return cls.memory

    @classmethod
    def save(cls, key, value):
        """
        Save a new value in the memory
        :param key: key to save
        :param value: value to save into the key
        """
        if key in cls.memory:
            logger.debug("[Recordatio] key %s already present in memory with value %s. Will be overridden"
                         % (key, cls.memory[key]))
        logger.debug("[Recordatio] key saved in memory. key: %s, value: %s" % (key, value))
        cls.memory[key] = value

    @classmethod
    def get_from_key(cls, key):
        try:
            return cls.memory[key]
        except KeyError:
            logger.debug("[Recordatio] key %s does not exist in memory" % key)
            return None

    @classmethod
    def add_parameters_from_order(cls, dict_parameter):
        logger.debug("[Recordatio] place parameters in temp list: %s" % dict_parameter)
        cls.temp.update(dict_parameter)

    @classmethod
    def clean_parameter_from_order(cls):
        """
        Clean the temps memory that store parameters loaded from vocal order
        """
        logger.debug("[Recordatio] Clean temp memory")
        cls.temp = dict()

    @classmethod
    def save_action_parameter_in_memory(cls, odie_memory_dict, action_parameters):
        """
        receive a dict of value send by the child action
        save in odie memory all value
        E.g
        dict_parameter_to_save = {"my_key_to_save_in_memory": "{{ output_val_from_action }}"}
        action_parameter = {"output_val_from_action": "this_is_a_value" }
        then the recordatio will save in memory the key "my_key_to_save_in_memory" and attach the value "this_is_a_value"
        :param action_parameters: dict of parameter the action has processed and send to the actione module to
                be processed by the TTS engine
        :param odie_memory_dict: a dict of key value the user want to save from the dict_action_parameter
        """

        if odie_memory_dict is not None:
            logger.debug("[Recordatio] save_memory - User want to save: %s" % odie_memory_dict)
            logger.debug("[Recordatio] save_memory - Available parameters in the action: %s" % action_parameters)

            for key, value in odie_memory_dict.items():
                # ask the recordatio to save in memory the target "key" if it was in parameters of the action
                if isinstance(action_parameters, dict):
                    if Utils.is_containing_bracket(value):
                        value = jinja2.Template(value).render(action_parameters)
                    Recordatio.save(key, value)

    @classmethod
    def save_parameter_from_order_in_memory(cls, order_parameters):
        """
        Save key from the temp dict (where parameters loaded from the voice order where placed temporary)
        into the memory dict
        :param order_parameters: dict of key to save.  {'key_name_in_memory': 'key_name_in_temp_dict'}
        :return True if a value has been saved in the odie memory
        """
        order_saved = False
        if order_parameters is not None:
            logger.debug("[Recordatio] save_parameter_from_order_in_memory - User want to save: %s" % order_parameters)
            logger.debug("[Recordatio] save_parameter_from_order_in_memory - Available parameters in orders: %s"
                         % cls.temp)

            for key, value in order_parameters.items():
                # ask the recordatio to save in memory the target "key" if it was in the order
                if Utils.is_containing_bracket(value):
                    # if the key exist in the temp dict we can load it with jinja
                    value = jinja2.Template(value).render(Recordatio.temp)
                    if value:
                        Recordatio.save(key, value)
                        order_saved = True

        return order_saved
