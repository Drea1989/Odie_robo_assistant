import logging
from odie.core.ActionModule import ActionModule
from odie.actions.alphabot.AlphaBot import AlphaBot

logging.basicConfig()
logger = logging.getLogger("odie")


class Initialiserover(ActionModule):
    def __init__(self, **kwargs):
        super(Initialiserover, self).__init__(**kwargs)

        AB = AlphaBot()
        AB.setMotor(0, 0)
