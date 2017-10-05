import logging

from odie import Utils
from odie.cues.order import Order

logging.basicConfig()
logger = logging.getLogger("odie")


class CueLauncher:

    # keep a list of instantiated cues
    list_launched_cues = list()

    def __init__(self):
        pass

    @classmethod
    def launch_cue_class_by_name(cls, cue_name, settings=None):
        """
        load the cue class from the given name, pass the brain and settings to the cue
        :param cue_name: name of the cue class to load
        :param settings: Settings Object
        """
        cue_folder = None
        if settings.resources:
            cue_folder = settings.resources.cue_folder

        launched_cue = Utils.get_dynamic_class_instantiation(package_name="cues",
                                                             module_name=cue_name,
                                                             resources_dir=cue_folder)

        cls.add_launched_cues_to_list(launched_cue)

        return launched_cue

    @classmethod
    def add_launched_cues_to_list(cls, cue):
        cls.list_launched_cues.append(cue)

    @classmethod
    def get_launched_cues_list(cls):
        return cls.list_launched_cues

    @classmethod
    def get_order_instance(cls):
        """
        Return the Order instance from the list of launched cues if exist
        :return:
        """
        for cue in cls.list_launched_cues:
            if isinstance(cue, Order):
                return cue
        return None
