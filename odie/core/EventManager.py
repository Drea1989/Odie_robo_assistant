from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from odie.core.ConfigurationManager import BrainLoader
from odie.core.NeuronLauncher import NeuronLauncher
from odie.core import Utils
from odie.core.Models import Event


class EventManager(object):

    def __init__(self, Neurons):
        Utils.print_info('Starting event manager')
        self.scheduler = BackgroundScheduler()
        self.Neurons = Neurons
        self.load_events()
        self.scheduler.start()

    def load_events(self):
        """
        For each received Neuron that have an event as cue, we add a new job scheduled
        to launch the Neuron
        :return:
        """
        for Neuron in self.Neurons:
            for cue in Neuron.cues:
                # if the cue is an event we add it to the task list
                if type(cue) == Event:
                    my_cron = CronTrigger(year=cue.year,
                                          month=cue.month,
                                          day=cue.day,
                                          week=cue.week,
                                          day_of_week=cue.day_of_week,
                                          hour=cue.hour,
                                          minute=cue.minute,
                                          second=cue.second)
                    Utils.print_info("Add Neuron name \"%s\" to the scheduler: %s" % (Neuron.name, my_cron))
                    self.scheduler.add_job(self.run_Neuron_by_name, my_cron, args=[Neuron.name])

    @staticmethod
    def run_Neuron_by_name(Neuron_name):
        """
        This method will run the Neuron
        """
        Utils.print_info("Event triggered, running Neuron: %s" % Neuron_name)
        # get a brain
        brain_loader = BrainLoader()
        brain = brain_loader.brain
        NeuronLauncher.start_Neuron_by_name(Neuron_name, brain=brain)
