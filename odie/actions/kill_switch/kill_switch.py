import sys

from odie.core.ActionModule import ActionModule


class Kill_switch(ActionModule):
    """
    Class used to exit odie process from system command
    """
    def __init__(self, **kwargs):
        super(Kill_switch, self).__init__(**kwargs)
        sys.exit()
