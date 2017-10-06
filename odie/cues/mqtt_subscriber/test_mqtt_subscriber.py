import unittest

from odie.core.Models import Action, Cue, Neuron, Brain
from odie.cues.mqtt_subscriber import Mqtt_subscriber
from odie.cues.mqtt_subscriber.models import Broker, Topic


class TestMqtt_subscriber(unittest.TestCase):

    def test_check_mqtt_dict(self):

        valid_dict_of_parameters = {
            "topic": "my_topic",
            "broker_ip": "192.168.0.1"
        }

        invalid_dict_of_parameters = {
            "topic": "my_topic"
        }

        self.assertTrue(Mqtt_subscriber.check_mqtt_dict(valid_dict_of_parameters))
        self.assertFalse(Mqtt_subscriber.check_mqtt_dict(invalid_dict_of_parameters))

    def test_get_list_neuron_with_mqtt_subscriber(self):

        # test with one cue mqtt
        action = Action(name='say', parameters={'message': ['test message']})
        cue1 = Cue(name="mqtt_subscriber", parameters={"topic": "test", "broker_ip": "192.168.0.1"})
        neuron1 = Neuron(name="neuron1", actions=[action], cues=[cue1])
        neurons = [neuron1]
        brain = Brain()
        brain.neurons = neurons

        expected_result = neurons

        mq = Mqtt_subscriber(brain=brain)

        generator = mq.get_list_neuron_with_mqtt_subscriber(brain)

        self.assertEqual(expected_result, list(generator))

        # test with two neuron
        action = Action(name='say', parameters={'message': ['test message']})
        cue1 = Cue(name="order", parameters="test_order")
        cue2 = Cue(name="mqtt_subscriber", parameters={"topic": "test", "broker_ip": "192.168.0.1"})
        neuron1 = Neuron(name="neuron1", actions=[action], cues=[cue1])
        neuron2 = Neuron(name="neuron2", actions=[action], cues=[cue1, cue2])

        neurons = [neuron1, neuron2]
        brain = Brain()
        brain.neurons = neurons

        expected_result = [neuron2]

        mq = Mqtt_subscriber(brain=brain)
        generator = mq.get_list_neuron_with_mqtt_subscriber(brain)

        self.assertEqual(expected_result, list(generator))

    def test_get_list_broker_to_instantiate(self):
        # ----------------
        # only one neuron
        # ----------------
        action = Action(name='say', parameters={'message': ['test message']})
        cue1 = Cue(name="mqtt_subscriber", parameters={"topic": "topic1", "broker_ip": "192.168.0.1"})
        neuron1 = Neuron(name="neuron1", actions=[action], cues=[cue1])
        brain = Brain()
        brain.neurons = [neuron1]

        list_neuron_with_mqtt_subscriber = [neuron1]

        expected_broker = Broker()
        expected_broker.broker_ip = "192.168.0.1"
        expected_broker.topics = list()
        expected_topic = Topic()
        expected_topic.name = "topic1"
        # add the current neuron to the topic
        expected_topic.neurons = list()
        expected_topic.neurons.append(neuron1)
        expected_broker.topics.append(expected_topic)

        expected_retuned_list = [expected_broker]

        mq = Mqtt_subscriber(brain=brain)

        self.assertListEqual(expected_retuned_list,
                             mq.get_list_broker_to_instantiate(list_neuron_with_mqtt_subscriber))

        # ----------------
        #  one neuron, two different broker
        # ----------------
        action = Action(name='say', parameters={'message': ['test message']})
        cue1 = Cue(name="mqtt_subscriber", parameters={"topic": "topic1",
                                                       "broker_ip": "192.168.0.1",
                                                       "is_json": False})
        cue2 = Cue(name="mqtt_subscriber", parameters={"topic": "topic2",
                                                       "broker_ip": "172.16.0.1",
                                                       "is_json": False})
        neuron1 = Neuron(name="neuron1", actions=[action], cues=[cue1, cue2])
        brain = Brain()
        brain.neurons = [neuron1]

        list_neuron_with_mqtt_subscriber = [neuron1]

        expected_broker1 = Broker()
        expected_broker1.broker_ip = "192.168.0.1"
        expected_broker1.topics = list()
        expected_topic = Topic()
        expected_topic.name = "topic1"
        # add the current neuron to the topic
        expected_topic.neurons = list()
        expected_topic.neurons.append(neuron1)
        expected_broker1.topics.append(expected_topic)

        expected_broker2 = Broker()
        expected_broker2.broker_ip = "172.16.0.1"
        expected_broker2.topics = list()
        expected_topic = Topic()
        expected_topic.name = "topic2"
        # add the current neuron to the topic
        expected_topic.neurons = list()
        expected_topic.neurons.append(neuron1)
        expected_broker2.topics.append(expected_topic)

        expected_retuned_list = [expected_broker1, expected_broker2]

        mq = Mqtt_subscriber(brain=brain)

        self.assertEqual(expected_retuned_list, mq.get_list_broker_to_instantiate(list_neuron_with_mqtt_subscriber))

        # ----------------
        #  two neuron, same broker, different topics
        # ----------------
        # neuron 1
        action1 = Action(name='say', parameters={'message': ['test message']})
        cue1 = Cue(name="mqtt_subscriber", parameters={"topic": "topic1", "broker_ip": "192.168.0.1"})
        neuron1 = Neuron(name="neuron1", actions=[action1], cues=[cue1])

        # neuron 2
        action2 = Action(name='say', parameters={'message': ['test message']})
        cue2 = Cue(name="mqtt_subscriber", parameters={"topic": "topic2", "broker_ip": "192.168.0.1"})
        neuron2 = Neuron(name="neuron2", actions=[action2], cues=[cue2])

        brain = Brain()
        brain.neurons = [neuron1, neuron2]

        list_neuron_with_mqtt_subscriber = [neuron1, neuron2]

        expected_broker1 = Broker()
        expected_broker1.broker_ip = "192.168.0.1"
        expected_broker1.topics = list()
        expected_topic1 = Topic()
        expected_topic1.name = "topic1"
        expected_topic2 = Topic()
        expected_topic2.name = "topic2"
        # add the current neuron to the topic
        expected_topic1.neurons = [neuron1]
        expected_topic2.neurons = [neuron2]
        # add both topic to the broker
        expected_broker1.topics.append(expected_topic1)
        expected_broker1.topics.append(expected_topic2)

        expected_retuned_list = [expected_broker1]

        mq = Mqtt_subscriber(brain=brain)

        self.assertEqual(expected_retuned_list, mq.get_list_broker_to_instantiate(list_neuron_with_mqtt_subscriber))

        # ----------------
        #  two neuron, same broker, same topic
        # ----------------
        # neuron 1
        action1 = Action(name='say', parameters={'message': ['test message']})
        cue1 = Cue(name="mqtt_subscriber", parameters={"topic": "topic1", "broker_ip": "192.168.0.1"})
        neuron1 = Neuron(name="neuron1", actions=[action1], cues=[cue1])

        # neuron 2
        action2 = Action(name='say', parameters={'message': ['test message']})
        cue2 = Cue(name="mqtt_subscriber", parameters={"topic": "topic1", "broker_ip": "192.168.0.1"})
        neuron2 = Neuron(name="neuron2", actions=[action2], cues=[cue2])

        brain = Brain()
        brain.neurons = [neuron1, neuron2]

        list_neuron_with_mqtt_subscriber = [neuron1, neuron2]

        expected_broker1 = Broker()
        expected_broker1.broker_ip = "192.168.0.1"
        expected_broker1.topics = list()
        expected_topic1 = Topic()
        expected_topic1.name = "topic1"
        # add both neurons to the topic
        expected_topic1.neurons = [neuron1, neuron2]
        # add the topic to the broker
        expected_broker1.topics.append(expected_topic1)

        expected_retuned_list = [expected_broker1]

        mq = Mqtt_subscriber(brain=brain)

        self.assertEqual(expected_retuned_list, mq.get_list_broker_to_instantiate(list_neuron_with_mqtt_subscriber))


if __name__ == '__main__':
    unittest.main()

    # suite = unittest.TestSuite()
    # suite.addTest(TestMqtt_subscriber("test_get_list_broker_to_instantiate"))
    # runner = unittest.TextTestRunner()
    # runner.run(suite)
