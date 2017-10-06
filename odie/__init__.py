#!/usr/bin/env python
# coding: utf8
import argparse
import logging
import time

from odie.core import ShellGui
from odie.core import Utils
from odie.core.ConfigurationManager import SettingLoader
from odie.core.ConfigurationManager.BrainLoader import BrainLoader
from odie.core.Utils.RpiUtils import RpiUtils
from odie.core.CueLauncher import CueLauncher
from flask import Flask
from ._version import version_str
# to check keyboard input
import signal
import sys

from odie.core.ResourcesManager import ResourcesManager
from odie.core.NeuronLauncher import NeuronLauncher

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
ACTION_LIST = ["start", "gui", "install", "uninstall", "cloud"]


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
    parser.add_argument("--cue-name", help="Cue name to uninstall")
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
        if not parser.action_name \
                and not parser.stt_name \
                and not parser.tts_name \
                and not parser.wakeon_name\
                and not parser.cue_name:
            Utils.print_danger("You must specify a module name with "
                               "--action-name "
                               "or --stt-name "
                               "or --tts-name "
                               "or --wakeon-name "
                               "or --cue-name")
            sys.exit(1)
        else:
            res_manager = ResourcesManager()
            res_manager.uninstall(action_name=parser.action_name,
                                  stt_name=parser.stt_name,
                                  tts_name=parser.tts_name,
                                  wakeon_name=parser.wakeon_name,
                                  cue_name=parser.cue_name)
        return

    # load the brain once
    brain_loader = BrainLoader(file_path=brain_file)
    brain = brain_loader.brain

    # load settings
    # get global configuration once
    settings_loader = SettingLoader()
    settings = settings_loader.settings

    # starting Odie
    if parser.action == "start":
        # create postgres brain table
        if settings.postgres:
            pg = settings.postgres
            from odie.postgres.PostgreManager import PostgresManager as PgManager
            Bsaved = PgManager.save_brain_table(pg=pg, brain=brain)
            if Bsaved:
                Utils.print_info("postgresql brain saved successfully")
        else:
            Utils.print_danger("no PostgreSQL configuration found")

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
            # start rest api
            start_rest_api(settings, brain)
            start_odie(settings, brain)

    if parser.action == "gui":
        try:
            ShellGui(brain=brain)
        except (KeyboardInterrupt, SystemExit):
            Utils.print_info("Ctrl+C pressed. Killing odie")
            sys.exit(0)

    if parser.action == "cloud":
        # Cloud API
        from odie_cloud.CloudFlaskAPI import CloudFlaskAPI
        if settings.rpi_settings:
            # init GPIO once
            RpiUtils(settings.rpi_settings)

        Utils.print_info("Starting Cloud REST API Listening port: %s" % settings.rest_api.port)
        # then start odie
        Utils.print_success("Starting odie Cloud")
        Utils.print_info("Press Ctrl+C for stopping")
        # catch signal for killing on Ctrl+C pressed
        signal.signal(signal.SIGINT, signal_handler)
        # start the state machine
        try:
            app = Flask(__name__)
            flask_api = CloudFlaskAPI(app=app,
                                      port=settings.rest_api.port,
                                      brain=brain,
                                      allowed_cors_origin=settings.rest_api.allowed_cors_origin)
            flask_api.start()
        except (KeyboardInterrupt, SystemExit):
            Utils.print_info("Ctrl+C pressed. Killing odie Cloud")
        finally:
            # we need to switch GPIO pin to default status if we are using a Rpi
            if settings.rpi_settings:
                logger.debug("Clean GPIO")
                import RPi.GPIO as GPIO
                GPIO.cleanup()


class AppFilter(logging.Filter):
    """
    Class used to add a custom entry into the logger
    """
    def filter(self, record):
        record.app_version = "odie-%s" % version_str
        return True


def configure_logging(debug=None):
    """
    Prepare log folder in current home directory.

    :param debug: If true, set the log level to debug

    """
    logger = logging.getLogger("odie")
    logger.addFilter(AppFilter())
    logger.propagate = False
    syslog = logging.StreamHandler()
    syslog .setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s :: %(app_version)s :: %(message)s', "%Y-%m-%d %H:%M:%S")
    syslog .setFormatter(formatter)

    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # add the handlers to logger
    logger.addHandler(syslog)
    logger.debug("Logger ready")


def get_list_cue_class_to_load(brain):
    """
    Return a list of cue class name
    For all neuron, each cue type is added to a list only if the cue is not yet present in the list
    :param brain: Brain object
    :type brain: Brain
    :return: set of cue class
    """
    list_cue_class_name = set()

    for neuron in brain.neurons:
        for cue_object in neuron.cues:
            list_cue_class_name.add(cue_object.name)
    logger.debug("[Odie entrypoint] List of cue class to load: %s" % list_cue_class_name)
    return list_cue_class_name


def start_rest_api(settings, brain):
    """
    Start the Rest API if asked in the user settings
    """
    # run the api if the user want it
    from odie.core.RestAPI.FlaskAPI import FlaskAPI
    if settings.rest_api.active:
        Utils.print_info("Starting REST API Listening port: %s" % settings.rest_api.port)
        app = Flask(__name__)
        flask_api = FlaskAPI(app=app,
                             port=settings.rest_api.port,
                             brain=brain,
                             allowed_cors_origin=settings.rest_api.allowed_cors_origin)
        flask_api.daemon = True
        flask_api.start()


def start_odie(settings, brain):
    """
    Start all cues declared in the brain
    """
    # start odiee
    Utils.print_success("Starting Odiee")
    Utils.print_info("Press Ctrl+C for stopping")
    # catch signal for killing on Ctrl+C pressed
    signal.signal(signal.SIGINT, signal_handler)

    # get a list of cue class to load from declared neuron in the brain
    # this list will contain string of cue class type.
    # For example, if the brain contains multiple time the cue type "order", the list will be ["order"]
    # If the brain contains some neuron with "order" and "event", the list will be ["order", "event"]
    list_cues_class_to_load = get_list_cue_class_to_load(brain)

    # start each class name
    try:
        for cue_class_name in list_cues_class_to_load:
            cue_instance = CueLauncher.launch_cue_class_by_name(cue_name=cue_class_name,
                                                                settings=settings)
            if cue_instance is not None:
                cue_instance.daemon = True
                cue_instance.start()

        while True:  # keep main thread alive
            time.sleep(0.1)

    except (KeyboardInterrupt, SystemExit):
        # we need to switch GPIO pin to default status if we are using a Rpi
        if settings.rpi_settings:
            Utils.print_info("GPIO cleaned")
            logger.debug("Clean GPIO")
            import RPi.GPIO as GPIO
            GPIO.cleanup()
