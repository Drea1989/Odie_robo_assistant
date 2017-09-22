#!/usr/bin/env python
# coding: utf8
import argparse
import logging

from odie.core import ShellGui
from odie.core import Utils
from odie.core.ConfigurationManager import SettingLoader
from odie.core.ConfigurationManager.BrainLoader import BrainLoader
from odie.core.EventManager import EventManager
from odie.core.MainController import MainController
from odie.core.Utils.RpiUtils import RpiUtils
from odie.core.Utils.PostgreManager import PostgresManager as PgManager

from ._version import version_str
#to check keyboard input
import signal
import sys

from odie.core.ResourcesManager import ResourcesManager
from odie.core.NeuronLauncher import NeuronLauncher
from odie.core.OrderAnalyser import OrderAnalyser

logging.basicConfig()
logger = logging.getLogger("odie")


def signal_handler(signal, frame):
    """
    Used to catch a keyboard signal like Ctrl+C in order to kill the odie program.

    :param signal: signal handler
    :param frame: execution frame

    """
    print("\n")
    Utils.print_info("Ctrl+C pressed. Killing odie")
    sys.exit(0)

# actions available
ACTION_LIST = ["start", "gui", "install", "uninstall","cloud"]


def parse_args(args):
    """
    Parsing function
    :param args: arguments passed from the command line
    :return: return parser
    """
    # create arguments
    parser = argparse.ArgumentParser(description='odie')
    parser.add_argument("action", help="[start|gui|install|uninstall]")
    parser.add_argument("--run-neuron",
                        help="Name of a neuron to load surrounded by quote")
    parser.add_argument("--run-order", help="order surrounded by a quote")
    parser.add_argument("--brain-file", help="Full path of a brain file")
    parser.add_argument("--debug", action='store_true',
                        help="Show debug output")
    parser.add_argument("--git-url", help="Git URL of the neuron to install")
    parser.add_argument("--action-name", help="action name to uninstall")
    parser.add_argument("--stt-name", help="STT name to uninstall")
    parser.add_argument("--tts-name", help="TTS name to uninstall")
    parser.add_argument("--wakeon-name", help="Wakeon name to uninstall")
    parser.add_argument('-v', '--version', action='version',
                        version='odie ' + version_str)

    # parse arguments from script parameters
    return parser.parse_args(args)


def main():
    """Entry point of odie program."""
    # parse argument. the script name is removed
    try:
        parser = parse_args(sys.argv[1:])
    except SystemExit:
        sys.exit(1)

    # check if we want debug
    configure_logging(debug=parser.debug)

    logger.debug("odie args: %s" % parser)

    # by default, no brain file is set.
    # Use the default one: brain.yml in the root path
    brain_file = None

    # check if user set a brain.yml file
    if parser.brain_file:
        brain_file = parser.brain_file

    # check the user provide a valid action
    if parser.action not in ACTION_LIST:
        Utils.print_warning("%s is not a recognised action\n" % parser.action)
        sys.exit(1)

    # install modules
    if parser.action == "install":
        if not parser.git_url:
            Utils.print_danger("You must specify the git url")
            sys.exit(1)
        else:
            parameters = {
                "git_url": parser.git_url
            }
            res_manager = ResourcesManager(**parameters)
            res_manager.install()
        return

    # uninstall modules
    if parser.action == "uninstall":
        if not parser.action_name and not parser.stt_name and not parser.tts_name and not parser.wakeon_name:
            Utils.print_danger("You must specify a module name with --action-name or --stt-name or --tts-name "
                               "or --wakeon-name")
            sys.exit(1)
        else:
            res_manager = ResourcesManager()
            res_manager.uninstall(action_name=parser.action_name, stt_name=parser.stt_name,
                                  tts_name=parser.tts_name, wakeon_name=parser.wakeon_name)
        return

    # load the brain once
    brain_loader = BrainLoader(file_path=brain_file)
    brain = brain_loader.brain

    # load settings
    # get global configuration once
    settings_loader = SettingLoader()
    settings = settings_loader.settings

    #create postgres brain table
    if settings.postgres:
        pg = settings.postgres
        Bsaved = PgManager.save_brain_table(pg = pg,brain = brain)
        if Bsaved:
            Utils.print_info("postgresql brain saved successfully")
    else:
        Utils.print_danger("no PostgreSQL configuration found")
    


    #starting Odie
    if parser.action == "start":

        if settings.rpi_settings:
            # init GPIO once
            RpiUtils(settings.rpi_settings)

        # user set a neuron to start
        if parser.run_neuron is not None:
            NeuronLauncher.start_neuron_by_name(parser.run_neuron,
                                                  brain=brain)

        if parser.run_order is not None:
            NeuronLauncher.run_matching_neuron_from_order(parser.run_order,
                                                            brain=brain,
                                                            settings=settings,
                                                            is_api_call=False)

        if (parser.run_neuron is None) and (parser.run_order is None):
            # first, load events in event manager
            EventManager(brain.neurons)
            Utils.print_success("Events loaded")
            # then start odie
            Utils.print_success("Starting odie")
            Utils.print_info("Press Ctrl+C for stopping")
            # catch signal for killing on Ctrl+C pressed
            signal.signal(signal.SIGINT, signal_handler)
            # start the state machine
            try:
                MainController(brain=brain)
            except (KeyboardInterrupt, SystemExit):
                Utils.print_info("Ctrl+C pressed. Killing odie")
            finally:
                # we need to switch GPIO pin to default status if we are using a Rpi
                if settings.rpi_settings:
                    logger.debug("Clean GPIO")
                    import RPi.GPIO as GPIO
                    GPIO.cleanup()

    if parser.action == "gui":
        try:
            ShellGui(brain=brain)
        except (KeyboardInterrupt, SystemExit):
            Utils.print_info("Ctrl+C pressed. Killing odie")
            sys.exit(0)

    if parser.action == "cloud":
        if settings.rpi_settings:
            # init GPIO once
            RpiUtils(settings.rpi_settings)
        # load the brain once
        CloudBrain_loader = BrainLoader(file_path=brain_file)
        CloudBrain = CloudBrain_loader.brain
        # then start odie
        Utils.print_success("Starting odie Cloud")
        Utils.print_info("Press Ctrl+C for stopping")
        # catch signal for killing on Ctrl+C pressed
        signal.signal(signal.SIGINT, signal_handler)
        # start the state machine
        try:
            CloudFlaskAPI(brain=CloudBrain)
        except (KeyboardInterrupt, SystemExit):
            Utils.print_info("Ctrl+C pressed. Killing odie")
        finally:
            # we need to switch GPIO pin to default status if we are using a Rpi
            if settings.rpi_settings:
                logger.debug("Clean GPIO")
                import RPi.GPIO as GPIO
                GPIO.cleanup()



def configure_logging(debug=None):
    """
    Prepare log folder in current home directory.

    :param debug: If true, set the log level to debug

    """
    logger = logging.getLogger("odie")
    logger.propagate = False
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    ch.setFormatter(formatter)

    # add the handlers to logger
    logger.addHandler(ch)

    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.debug("Logger ready")