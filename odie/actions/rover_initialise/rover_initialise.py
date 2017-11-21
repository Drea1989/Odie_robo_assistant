import logging
from odie.core.ActionModule import ActionModule
from odie.actions.utils.AlphaBot import AlphaBot

logging.basicConfig()
logger = logging.getLogger("odie")


class Rover_initialise(ActionModule):
    def __init__(self, **kwargs):
        super(Rover_initialise, self).__init__(**kwargs)

        AB = AlphaBot()
        AB.setMotor(0, 0)
