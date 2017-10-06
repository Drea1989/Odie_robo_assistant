import logging

from odie.core.ConfigurationManager import BrainLoader
from odie.core.LIFOBuffer import LIFOBuffer
from odie.core.Models.MatchedNeuron import MatchedNeuron
from odie.core.ActionLauncher import ActionLauncher
from odie.core.OrderAnalyser import OrderAnalyser


logging.basicConfig()
logger = logging.getLogger("odie")


class NeuronNameNotFound(Exception):
    """
    The Neuron has not been found

    .. seealso: Neuron
    """
    pass


class NeuronLauncher(object):

    @classmethod
    def start_neuron_by_name(cls, name, brain=None, overriding_parameter_dict=None):
        """
        Start a neuron by it's name
        :param name: Name (Unique ID) of the neuron to launch
        :param brain: Brain instance
        :param overriding_parameter_dict: parameter to pass to actions
        """
        logger.debug("[NeuronLauncher] start_neuron_by_name called with neuron name: %s " % name)
        # check if we have found and launched the neuron
        neuron = brain.get_neuron_by_name(neuron_name=name)

        if not neuron:
            raise NeuronNameNotFound("The neuron name \"%s\" does not exist in the brain file" % name)
        else:
            # get our singleton LIFO
            lifo_buffer = LIFOBuffer()
            list_neuron_to_process = list()
            new_matching_neuron = MatchedNeuron(matched_neuron=neuron,
                                                matched_order=None,
                                                user_order=None,
                                                overriding_parameter=overriding_parameter_dict)
            list_neuron_to_process.append(new_matching_neuron)
            lifo_buffer.add_neuron_list_to_lifo(list_neuron_to_process)
            return lifo_buffer.execute(is_api_call=True)

    @classmethod
    def run_matching_neuron_from_order(cls, order_to_process, brain, settings, is_api_call=False, no_voice=False):
        """
        :param order_to_process: the spoken order sent by the user
        :param brain: Brain object
        :param settings: Settings object
        :param is_api_call: if True, the current call come from the API. This info must be known by launched Action
        :param no_voice: If true, the generated text will not be processed by the TTS engine
        :return: list of matched neuron
        """

        # get our singleton LIFO
        lifo_buffer = LIFOBuffer()

        # if the LIFO is not empty, so, the current order is passed to the current processing neuron as an answer
        if len(lifo_buffer.lifo_list) > 0:
            # the LIFO is not empty, this is an answer to a previous call
            return lifo_buffer.execute(answer=order_to_process, is_api_call=is_api_call, no_voice=no_voice)

        else:  # the LIFO is empty, this is a new call
            # get a list of matched neuron from the order
            list_neuron_to_process = OrderAnalyser.get_matching_neuron(order=order_to_process, brain=brain)

            if not list_neuron_to_process:  # the order analyser returned us an empty list
                # add the default neuron if exist into the lifo
                if settings.default_neuron:
                    logger.debug("[NeuronLauncher] No matching Neuron-> running default neuron ")
                    # get the default neuron
                    default_neuron = brain.get_neuron_by_name(settings.default_neuron)
                    new_matching_neuron = MatchedNeuron(matched_neuron=default_neuron,
                                                        matched_order=None,
                                                        user_order=order_to_process)
                    list_neuron_to_process.append(new_matching_neuron)
                else:
                    logger.debug("[NeuronLauncher] No matching Neuron and no default neuron ")

            lifo_buffer.add_neuron_list_to_lifo(list_neuron_to_process)
            lifo_buffer.api_response.user_order = order_to_process

            return lifo_buffer.execute(is_api_call=is_api_call, no_voice=no_voice)
