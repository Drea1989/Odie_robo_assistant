import logging
from threading import Thread

from odie.core.ConfigurationManager import BrainLoader
from odie.cues.mqtt_subscriber.MqttClient import MqttClient
from odie.cues.mqtt_subscriber.models import Broker, Topic

CLIENT_ID = "odie"

logging.basicConfig()
logger = logging.getLogger("odie")


class Mqtt_subscriber(Thread):

    def __init__(self, brain=None):
        super(Mqtt_subscriber, self).__init__()
        logger.debug("[Mqtt_subscriber] Mqtt_subscriber class created")
        # variables
        self.broker_ip = None
        self.topic = None
        self.json_message = False

        self.brain = brain
        if self.brain is None:
            self.brain = BrainLoader().get_brain()

    def run(self):
        logger.debug("[Mqtt_subscriber] Starting Mqtt_subscriber")
        # get the list of neuron that use Mqtt_subscriber as cue
        list_neuron_with_mqtt_subscriber = self.get_list_neuron_with_mqtt_subscriber(brain=self.brain)

        # we need to sort broker URL by ip, then for each broker, we sort by topic and attach neurons name to run to it
        list_broker_to_instantiate = self.get_list_broker_to_instantiate(list_neuron_with_mqtt_subscriber)

        # now instantiate a MQTT client for each broker object
        self.instantiate_mqtt_client(list_broker_to_instantiate)

    def get_list_neuron_with_mqtt_subscriber(self, brain):
        """
        return the list of neuron that use Mqtt_subscriber as cue in the provided brain
        :param brain: Brain object that contain all neurons loaded
        :type brain: Brain
        :return: list of neuron that use Mqtt_subscriber as cue
        """
        for neuron in brain.neurons:
            for cue in neuron.cues:
                # if the cue is an event we add it to the task list
                if cue.name == "mqtt_subscriber":
                    if self.check_mqtt_dict(cue.parameters):
                        yield neuron

    @staticmethod
    def check_mqtt_dict(mqtt_cue_parameters):
        """
        receive a dict of parameter from a mqtt_subscriber cue and them
        :param mqtt_cue_parameters: dict of parameters
        :return: True if parameters are valid
        """
        # check mandatory parameters
        mandatory_parameters = ["broker_ip", "topic"]
        if not all(key in mqtt_cue_parameters for key in mandatory_parameters):
            return False

        return True

    @staticmethod
    def get_list_broker_to_instantiate(list_neuron_with_mqtt_subscriber):
        """
        return a list of Broker object from the given list of neuron
        :param list_neuron_with_mqtt_subscriber: list of Neuron object
        :return: list of Broker
        """
        returned_list_of_broker = list()

        for neuron in list_neuron_with_mqtt_subscriber:
            for cue in neuron.cues:
                # check if the broker exist in the list
                if not any(x.broker_ip == cue.parameters["broker_ip"] for x in returned_list_of_broker):
                    logger.debug("[Mqtt_subscriber] Create new broker: %s" % cue.parameters["broker_ip"])
                    # create a new broker object
                    new_broker = Broker()
                    new_broker.build_from_cue_dict(cue.parameters)
                    # add the current topic
                    logger.debug("[Mqtt_subscriber] Add new topic to broker %s: %s" % (new_broker.broker_ip,
                                                                                       cue.parameters["topic"]))
                    new_topic = Topic()
                    new_topic.name = cue.parameters["topic"]
                    if "is_json" in cue.parameters:
                        logger.debug("[Mqtt_subscriber] Message for the topic %s will be json converted"
                                     % new_topic.name)
                        new_topic.is_json = bool(cue.parameters["is_json"])
                    else:
                        new_topic.is_json = False
                    # add the current neuron to the topic
                    new_topic.neurons = list()
                    new_topic.neurons.append(neuron)
                    new_broker.topics.append(new_topic)

                    logger.debug("[Mqtt_subscriber] Add new neuron to topic %s :%s" % (new_topic.name, neuron.name))
                    returned_list_of_broker.append(new_broker)
                else:
                    # the broker exist. get it from the list of broker
                    broker_to_edit = next((broker for broker in returned_list_of_broker
                                           if cue.parameters["broker_ip"] == broker.broker_ip))
                    # check if the topic already exist
                    if not any(topic.name == cue.parameters["topic"] for topic in broker_to_edit.topics):
                        new_topic = Topic()
                        new_topic.name = cue.parameters["topic"]
                        if "is_json" in cue.parameters:
                            logger.debug("[Mqtt_subscriber] Message for the topic %s will be json converted"
                                         % new_topic.name)
                            new_topic.is_json = bool(cue.parameters["is_json"])
                        else:
                            new_topic.is_json = False
                        logger.debug("[Mqtt_subscriber] Add new topic to existing broker "
                                     "%s: %s" % (broker_to_edit.broker_ip, cue.parameters["topic"]))
                        # add the current neuron to the topic
                        logger.debug("[Mqtt_subscriber] Add new neuron "
                                     "to topic %s :%s" % (new_topic.name, neuron.name))
                        new_topic.neurons = list()
                        new_topic.neurons.append(neuron)
                        # add the topic to the broker
                        broker_to_edit.topics.append(new_topic)
                    else:
                        # the topic already exist, get it from the list
                        topic_to_edit = next((topic for topic in broker_to_edit.topics
                                              if topic.name == cue.parameters["topic"]))
                        # add the neuron
                        logger.debug("[Mqtt_subscriber] Add neuron %s to existing topic %s "
                                     "in existing broker %s" % (neuron.name,
                                                                topic_to_edit.name,
                                                                broker_to_edit.broker_ip))
                        topic_to_edit.neurons.append(neuron)

        return returned_list_of_broker

    def instantiate_mqtt_client(self, list_broker_to_instantiate):
        """
        Instantiate a MqttClient thread for each broker
        :param list_broker_to_instantiate: list of broker to run
        """
        for broker in list_broker_to_instantiate:
            mqtt_client = MqttClient(broker=broker, brain=self.brain)
            mqtt_client.start()
