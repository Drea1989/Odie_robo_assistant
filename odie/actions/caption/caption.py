# import the necessary packages
from picamera import PiCamera
import time
import os
import requests
import logging
import json
try:  # attempt to use the Python 2 modules
    from urllib2 import URLError, HTTPError
except ImportError:  # use the Python 3 modules
    from urllib.error import URLError, HTTPError

from odie.core.ActionModule import ActionModule
from odie import SettingLoader

logging.basicConfig()
logger = logging.getLogger("odie")


class WaitTimeoutError(Exception):
    pass


class RequestError(Exception):
    pass


class UnknownValueError(Exception):
    pass


class Caption(ActionModule):
    def __init__(self, **kwargs):
        super(Caption, self).__init__(**kwargs)
        # get global configuration
        sl = SettingLoader()
        self.settings = sl.settings
        self.save_path = os.path.join(self.settings.cache_path, 'caption.jpg')
        # initialize the camera
        logger.debug("[Caption] setting camera up")
        with PiCamera() as camera:
            camera.resolution = (299, 299)
            camera.start_preview()
            # Camera warm-up time
            time.sleep(0.1)
            camera.capture(self.save_path)
        logger.debug("[Caption]picture taken at: {}".format(self.save_path))
        caption_file = open(self.save_path, 'rb')
        files = {'file': ('caption.jpg', caption_file, 'image/jpeg')}
        # TODO: replace with generic setting for odie cloud address
        host = '192.168.1.112:5000'
        url = "http://"+host+"/caption"
        try:
            request = requests.post(url, files=files, timeout=10)
            logger.debug("[Caption] request back, response: {}".format(request.json()))
            response = json.loads(request.text)["result"]
            err_code = request.status_code
        except HTTPError as e:
            raise RequestError("Caption request failed: {}".format(e.reason))
        except ConnectionError as e:
            raise RequestError("Caption connection failed: {}".format(e.reason))
        except URLError as e:
            raise RequestError("Caption connection failed: {}".format(e.reason))
        except Exception as e:
            raise RequestError("Caption connection failed: {}".format(str(e)))
        logger.debug("[Caption] the response is {}".format(response))
        # ignore any blank blocks
        if err_code in [200, 201]:
            logger.debug("[Caption] returning result")
            self.message = {str(response.keys()[0])}
            logger.debug("[Caption] returned message: %s" % str(self.message))

            self.say(self.message)
        else:
            raise RequestError("Caption request failed with: {}".format(err_code))
