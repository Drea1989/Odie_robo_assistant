# coding: utf8
import collections
from collections import Counter
import sys
import six

from odie.core.Models.MatchedNeuron import MatchedNeuron
from odie.core.Utils.Utils import Utils
from odie.core.Utils.PostgreManager import PostgresManager
from odie.core.ConfigurationManager import SettingLoader
from odie.core.Models import Order

import logging

logging.basicConfig()
logger = logging.getLogger("odie")


class OrderAnalyser:
    """
    This Class is used to get a list of neurons that match a given Spoken order
    """

    brain = None
    settings = None

    @classmethod
    def __init__(cls):
        cls.settings = SettingLoader().settings

    @classmethod
    def get_matching_neuron(cls, order, brain=None):
        """
        Return the list of matching neurons from the given order
        :param order: The user order
        :param brain: The loaded brain
        :return: The List of neurons matching the given order
        TODO: deprecate this function
        TODO: future release catch exception and run text summariser to try for a second time
        """
        cls.brain = brain
        logger.debug("[OrderAnalyser] Received order: %s" % order)
        if isinstance(order, six.binary_type):
            order = order.decode('utf-8')

        # We use a named tuple to associate the neuron and the cue of the neuron
        neuron_order_tuple = collections.namedtuple('tuple_neuron_matchingOrder',
                                                     ['neuron', 'order'])

        list_match_neuron = list()

        # if the received order is None we can stop the process immediately
        if order is None:
            return list_match_neuron

        # test each neuron from the brain
        for neuron in cls.brain.neurons:
            # we are only concerned by neuron with a order type of cue
            for cue in neuron.cues:
                if type(cue) == Order:
                    if cls.spelt_order_match_brain_order_via_table(cue.sentence, order):
                        # the order match the neuron, we add it to the returned list
                        logger.debug("Order found! Run neuron name: %s" % neuron.name)
                        Utils.print_success("Order matched in the brain. Running neuron \"%s\"" % neuron.name)
                        list_match_neuron.append(neuron_order_tuple(neuron=neuron, order=cue.sentence))

        # create a list of MatchedNeuron from the tuple list
        list_neuron_to_process = list()
        for tuple_el in list_match_neuron:
            new_matching_neuron = MatchedNeuron(matched_neuron=tuple_el.neuron,
                                                  matched_order=tuple_el.order,
                                                  user_order=order)
            list_neuron_to_process.append(new_matching_neuron)

        return list_neuron_to_process
    @classmethod
    def get_matching_neuron_new(cls, order, brain=None):
        """
        Return the list of matching neurons from the given order
        :param order: The user order
        :param brain: The loaded brain param brain is deprecated
        :return: The List of neurons matching the given order
        TODO: future release catch exception and run text summariser to try for a second time
        """
        logger.debug("[OrderAnalyser] Received order: %s" % order)
        if isinstance(order, six.binary_type):
            order = order.decode('utf-8')

        list_match_neuron = list()

        # if the received order is None we can stop the process immediately
        if order is None:
            return list_match_neuron

        #Get an order with bracket inside like: "hello my name is {{ name }}.
        #return a string without bracket like "hello my name is "
        matches = Utils.find_all_matching_brackets(order)
        for match in matches:
            order = order.replace(match, "")

        #connect to postgres
        pg = cls.settings.postgres
        conn = PostgresManager.get_connection(pg.host,pg.database,pg.user,pg.password)

        #TODO make postgres work
        #cur = conn.cursor()
        #cur.execute("SELECT name FROM brain WHERE to_tsvector(cues) @@ to_tsquery(%s) order by ts_rank"),(order))
        
        list_neuron_to_process = cur.fetchall() 

        #close connection
        cur.close()
        cunn.close()

        if list_neuron_to_process:
            logger.debug("Order found! Run neuron name: %s" % list_neuron_to_process)
            Utils.print_success("Order matched in the brain. Running neuron \"%s\"" % list_neuron_to_process)

        return list_neuron_to_process


    @classmethod
    def spelt_order_match_brain_order_via_table(cls, order_to_analyse, user_said):
        """
        return true if all formatted(_format_sentences_to_analyse(order_to_analyse, user_said)) strings
                that are in the sentence are present in the order to test.
        :param order_to_analyse: String order to test
        :param user_said: String to compare to the order
        :return: True if all string are present in the order
        TODO: to deprecate in favor of full text search
        """
        # Lowercase all incoming
        order_to_analyse = order_to_analyse.lower()
        user_said = user_said.lower()

        logger.debug("[spelt_order_match_brain_order_via_table] "
                     "order to analyse: %s, "
                     "user sentence: %s"
                     % (order_to_analyse, user_said))

        list_word_user_said = user_said.split()
        split_order_without_bracket = cls._get_split_order_without_bracket(order_to_analyse)

        # if all words in the list of what the user said is in the list of word in the order
        return cls._counter_subset(split_order_without_bracket, list_word_user_said)

    @staticmethod
    def _get_split_order_without_bracket(order):
        """
        Get an order with bracket inside like: "hello my name is {{ name }}.
        return a list of string without bracket like ["hello", "my", "name", "is"]
        :param order: sentence to split
        :return: list of string without bracket
        """

        matches = Utils.find_all_matching_brackets(order)
        for match in matches:
            order = order.replace(match, "")
        # then split
        split_order = order.split()
        return split_order

    @staticmethod
    def _counter_subset(list1, list2):
        """
        check if the number of occurrences matches
        :param list1:
        :param list2:
        :return:
        TODO: to deprecate in favor of full text search
        """
        c1, c2 = Counter(list1), Counter(list2)
        for k, n in c1.items():
            if n > c2[k]:
                return False
        return True
