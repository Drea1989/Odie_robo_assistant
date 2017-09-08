# -*- coding: utf-8 -*-
import logging
import wave

import pyaudio

from odie.core.PlayerModule import PlayerModule

logging.basicConfig()
logger = logging.getLogger("odie")

CHUNK = 1024


class Pyaudioplayer(PlayerModule):
    """
    This Class is representing the Player Object used to play the all sound of the system.
    """

    def __init__(self, **kwargs):
        super(Pyaudioplayer, self).__init__(**kwargs)
        logger.debug("[Pyaudioplayer.__init__] instance")
        logger.debug("[Pyaudioplayer.__init__] args : %s " % str(kwargs))

    def play(self, file_path):
        """
        Play the sound located in the provided file_path
        :param file_path: The file path of the sound to play. Must be wav format
        :type file_path: str              
        """
        if self.convert:
            self.convert_mp3_to_wav(file_path_mp3=file_path)
        # open the wave file
        wf = wave.open(file_path, 'rb')

        # instantiate PyAudio
        p = pyaudio.PyAudio()

        # open stream (2)
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        # frames_per_buffer=CHUNK,
                        output=True)

        # read data
        data = wf.readframes(CHUNK)

        logger.debug("Pyplayer file: %s" % str(file_path))

        # play stream (3)
        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(CHUNK)

        # stop stream (4)
        stream.stop_stream()
        stream.close()

        # close PyAudio
        p.terminate()
