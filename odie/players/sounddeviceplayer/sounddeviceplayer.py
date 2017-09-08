# -*- coding: utf-8 -*-
import logging

import sounddevice as sd
import soundfile as sf

from odie.core.PlayerModule import PlayerModule

logging.basicConfig()
logger = logging.getLogger("odie")

FS = 48000


class Sounddeviceplayer(PlayerModule):
    """
    This Class is representing the Player Object used to play the all sound of the system.
    """

    def __init__(self, **kwargs):
        super(Sounddeviceplayer, self).__init__(**kwargs)
        logger.debug("[Sounddeviceplayer.__init__] instance")
        logger.debug("[Sounddeviceplayer.__init__] args : %s " % str(kwargs))

    def play(self, file_path):

        if self.convert:
            self.convert_mp3_to_wav(file_path_mp3=file_path)
        data, fs = sf.read(file_path)
        sd.play(data, fs)
        sd.wait()
