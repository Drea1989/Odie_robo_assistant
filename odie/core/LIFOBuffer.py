import logging

from odie.core.ActionLauncher import ActionLauncher
from odie.core.Models import Singleton
from odie.core.Models.APIResponse import APIResponse

logging.basicConfig()
logger = logging.getLogger("odie")


class Serialize(Exception):
    """
    When raised, the LIFO class return the current API response to the caller
    """
    pass


class NeuronListAddedToLIFO(Exception):
    """
    When raised, a neuron list to process has been added to the LIFO list. 
    The LIFO must start over and process the last neuron list added
    """
    pass


class LIFOBuffer(object):
    """
    This class is a LIFO list of neuron to process where the last neuron list to enter will be the first neuron
    list to be processed.
    This design is needed in order to use Odie from the API. 
    Because we want to return an information when a Action is still processing and waiting for an answer from the user
    like with the Neurotransmitter action.
    
    """
    __metaclass__ = Singleton

    api_response = APIResponse()
    lifo_list = list()
    logger.debug("[LIFOBuffer] LIFO buffer created")
    answer = None
    is_api_call = False
    no_voice = False

    @classmethod
    def set_answer(cls, value):
        cls.answer = value

    @classmethod
    def set_api_call(cls, value):
        cls.is_api_call = value

    @classmethod
    def add_neuron_list_to_lifo(cls, matched_neuron_list):
        """
        Add a neuron list to process to the lifo
        :param matched_neuron_list: List of Matched Neuron
        :return: 
        """
        logger.debug("[LIFOBuffer] Add a new neuron list to process to the LIFO")
        cls.lifo_list.append(matched_neuron_list)

    @classmethod
    def clean(cls):
        """
        Clean the LIFO by creating a new list
        """
        cls.lifo_list = list()
        cls.api_response = APIResponse()

    @classmethod
    def _return_serialized_api_response(cls):
        """
        Serialize Exception has been raised by the execute process somewhere, return the serialized API response
        to the caller. Clean up the APIResponse object for the next call
        :return: 
        """
        # we prepare a json response
        returned_api_response = cls.api_response.serialize()
        # we clean up the API response object for the next call
        cls.api_response = APIResponse()
        return returned_api_response

    @classmethod
    def execute(cls, answer=None, is_api_call=False, no_voice=False):
        """
        Process the LIFO list.
        
        The LIFO list contains multiple list of matched neurons.        
        For each list of matched neuron we process neurons inside        
        For each neurons we process actions.        
        If a action add a Neuron list to the lifo, this neuron list is processed before executing the first list 
        in which we were in.
        
        :param answer: String answer to give the the last action which was waiting for an answer
        :param is_api_call: Boolean passed to all action in order to let them know if the current call comes from API
        :param no_voice: If true, the generated text will not be processed by the TTS engine
        :return: serialized APIResponse object
        """
        # store the answer if present
        cls.answer = answer
        cls.is_api_call = is_api_call
        cls.no_voice = no_voice

        try:
            # we keep looping over the LIFO til we have neuron list to process in it
            while cls.lifo_list:
                logger.debug("[LIFOBuffer] number of neuron list to process: %s" % len(cls.lifo_list))
                try:
                    # get the last list of matched neuron in the LIFO
                    last_neuron_fifo_list = cls.lifo_list[-1]
                    cls._process_neuron_list(last_neuron_fifo_list)
                except NeuronListAddedToLIFO:
                    continue
                # remove the neuron list from the LIFO
                cls.lifo_list.remove(last_neuron_fifo_list)
            raise Serialize

        except Serialize:
            return cls._return_serialized_api_response()

    @classmethod
    def _process_neuron_list(cls, neuron_list):
        """
        Process a list of matched neuron.
        Execute each action list for each neuron.
        Add info in the API response object after each processed neuron
        Remove the neuron from the neuron_list when it has been fully executed
        :param neuron_list: List of MatchedNeuron
        """
        # we keep processing til we have neuron in the FIFO to process
        while neuron_list:
            # get the first matched neuron in the list
            matched_neuron = neuron_list[0]
            # add the neuron to the API response so the user will get the status if the neuron was not already
            # in the response
            if matched_neuron not in cls.api_response.list_processed_matched_neuron:
                cls.api_response.list_processed_matched_neuron.append(matched_neuron)

            cls._process_action_list(matched_neuron=matched_neuron)

            # The neuron has been processed we can remove it from the list.
            neuron_list.remove(matched_neuron)

    @classmethod
    def _process_action_list(cls, matched_neuron):
        """
        Process the action list of the matched_neuron
        Execute the Action
        Executing a Action creates a ActionModule object. This one can have 3 status:
        - waiting for an answer: The action wait for an answer from the caller. The api response object is returned.
                                 The action is not removed from the matched neuron to be executed again
        - want to execute a neuron: The action add a list of neuron to execute to the lifo. 
                                     The LIFO restart over to process it.The action is removed from the matched neuron
        - complete: The action has been executed and its not waiting for an answer and doesn't want to start a neuron
                    The action is removed from the matched neuron
        :param matched_neuron: MatchedNeuron object to process
        """

        logger.debug("[LIFOBuffer] number of action to process: %s" % len(matched_neuron.action_fifo_list))
        # while we have neuron to process in the list of neuron
        while matched_neuron.action_fifo_list:
            # get the first action in the FIFO action list
            action = matched_neuron.action_fifo_list[0]
            # from here, we are back into the last action we were processing.
            if cls.answer is not None:  # we give the answer if exist to the first action
                action.parameters["answer"] = cls.answer
                # the next action should not get this answer
                cls.answer = None
            # todo fix this when we have a full client/server call. The client would be the voice or api call
            action.parameters["is_api_call"] = cls.is_api_call
            action.parameters["no_voice"] = cls.no_voice
            logger.debug("[LIFOBuffer] process_action_list: is_api_call: %s, no_voice: %s" % (cls.is_api_call,
                                                                                              cls.no_voice))
            # execute the action
            instantiated_action = ActionLauncher.start_action(action=action,
                                                              parameters_dict=matched_neuron.parameters)

            # the status of an execution is "complete" if no action are waiting for an answer
            cls.api_response.status = "complete"
            if instantiated_action is not None:
                if instantiated_action.is_waiting_for_answer:  # the action is waiting for an answer
                    logger.debug("[LIFOBuffer] Wait for answer mode")
                    cls.api_response.status = "waiting_for_answer"
                    raise Serialize
                else:
                    logger.debug("[LIFOBuffer] complete mode")
                    # we add the instantiated action to the action_module_list.
                    # This one contains info about generated text
                    matched_neuron.action_module_list.append(instantiated_action)
                    # the action is fully processed we can remove it from the list
                    matched_neuron.action_fifo_list.remove(action)

                if instantiated_action.pending_neuron:  # the last executed action want to run a neuron
                    logger.debug("[LIFOBuffer] Last executed action want to run a neuron. Restart the LIFO")
                    # add the neuron to the lifo (inside a list as expected by the lifo)
                    cls.add_neuron_list_to_lifo([instantiated_action.pending_neuron])
                    # we have added a list of neuron to the LIFO ! this one must start over.
                    # break all while loop until the execution is back to the LIFO loop
                    raise NeuronListAddedToLIFO
            else:
                raise Serialize
