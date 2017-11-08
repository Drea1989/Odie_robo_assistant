"""Library for performing speech recognition, with support for several engines and APIs, online and offline."""
import logging
import json
from speech_recognition import AudioData, AudioSource

try:  # attempt to use the Python 2 modules
    from urllib2 import URLError, HTTPError
except ImportError:  # use the Python 3 modules
    from urllib.error import URLError, HTTPError
import requests


logging.basicConfig()
logger = logging.getLogger("odie")


class WaitTimeoutError(Exception):
    pass


class RequestError(Exception):
    pass


class UnknownValueError(Exception):
    pass


class Recognizer(AudioSource):
    def __init__(self):
        """
        Creates a new ``Recognizer`` instance, which represents a collection of speech recognition functionality.
        """
        logger.debug("[OdieSTT recognizer] init")
        self.energy_threshold = 300  # minimum audio energy to consider for recording
        self.dynamic_energy_threshold = True
        self.dynamic_energy_adjustment_damping = 0.15
        self.dynamic_energy_ratio = 1.5
        self.pause_threshold = 0.8  # seconds of non-speaking audio before a phrase is considered complete
        self.operation_timeout = 10  # seconds after an internal operation (e.g., an API request) starts before it times out, or ``None`` for no timeout
        self.phrase_threshold = 0.3  # minimum seconds of speaking audio before we consider the speaking audio a phrase - values below this are ignored (for filtering out clicks and pops)
        self.non_speaking_duration = 0.5  # seconds of non-speaking audio to keep on both sides of the recording

    def recognize_odie(self, audio_data, key=None, language="en-US", host='192.168.1.112:5001'):
        """
        Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Odie Speech Recognition API.

        The Odie Speech Recognition API key is specified by ``key``. If not specified, it uses a generic key that works out of the box.
        This should generally be used for personal or testing purposes only, as it **may be revoked by Andrea Balzano at any time**.

        To obtain your own API key, contact Andrea Balzano at andrea.balzano@live.it

        The recognition language is determined by ``language``, an RFC5646 language tag like
        ``"en-US"`` (US English) or ``"fr-FR"`` (International French), defaulting to US English.
        A list of supported language tags can be found in this `StackOverflow answer <http://stackoverflow.com/a/14302134>`__.

        Returns the most likely transcription.

        Raises a ``speech_recognition.UnknownValueError`` exception if the speech is unintelligible. Raises a ``speech_recognition.RequestError``
        exception if the speech recognition operation failed, if the key isn't valid, or if there is no internet connection.
        """
        logger.debug("[OdieSTT recognizer] start recognizer")
        assert isinstance(audio_data, AudioData), "``audio_data`` must be audio data"
        assert key is None or isinstance(key, str), "``key`` must be ``None`` or a string"
        assert isinstance(language, str), "``language`` must be a string"

        flac_data = audio_data.get_flac_data(
            convert_rate=None if audio_data.sample_rate == 16000 else 16000,  # audio samples must be at 16 kHz
            convert_width=2  # audio samples must be 16-bit
        )
        logger.debug("[OdieSTT recognizer] audio ok")
        if key is None:
            key = "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"
        url = "http://"+host+"/speech/recognize"

        logger.debug("[OdieSTT recognizer] sending request")

        files = {'file': ('recognition.flac', flac_data, 'audio/x-flac')}
        payload = {"lang": language}
        # obtain audio transcription results
        try:
            request = requests.post(url, files=files, data=payload, timeout=self.operation_timeout)
            logger.debug("[OdieSTT recognizer] request back, response: {}".format(request.json()))
            response = json.loads(request.text)["result"]
            err_code = request.status_code
        except HTTPError as e:
            raise RequestError("recognition request failed: {}".format(e.reason))
        except ConnectionError as e:
            raise RequestError("recognition connection failed: {}".format(e.reason))
        except URLError as e:
            raise RequestError("recognition connection failed: {}".format(e.reason))
        except Exception as e:
            raise RequestError("recognition connection failed: {}".format(str(e)))
        logger.debug("[OdieSTT recognizer] the response is {}".format(response))
        # ignore any blank blocks
        if err_code in [200, 201]:
            logger.debug("[OdieSTT recognizer] returning result")
            return response
        else:
            raise RequestError("recognition request failed with: {}".format(err_code))
