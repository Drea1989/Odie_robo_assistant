import logging

from odie.core.ActionModule import ActionModule
from odie.actions.alphabot import AlphaBot

logging.basicConfig()
logger = logging.getLogger("odie")

class InitialiseRover(ActionModule):
    def __init__(self, **kwargs):
        super(InitialiseRover, self).__init__(**kwargs)

        AB = AlphaBot()
        AB.setMotor(0,0)