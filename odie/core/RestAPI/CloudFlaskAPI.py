import logging
import os
import threading

import time

from odie.core.Utils.FileManager import FileManager

from odie.core.ConfigurationManager import SettingLoader, BrainLoader
from werkzeug.utils import secure_filename

from flask import jsonify
from flask import request
from flask_restful import abort
from flask_cors import CORS

from odie.core.RestAPI.utils import requires_auth
from odie._version import version_str

logging.basicConfig()
logger = logging.getLogger("odie")

AUDIO_UPLOAD_FOLDER = '/tmp/odie_cloud/tmp_uploaded_audio'
VIDEO_UPLOAD_FOLDER = '/tmp/odie_cloud/tmp_uploaded_video'
FAIL_UPLOAD_FOLDER = '/tmp/odie_cloud/tmp_uploaded_failed_interactions'
ALLOWED_EXTENSIONS = {'mp3', 'wav','flac','jpg'}


class FlaskAPI(threading.Thread):
    def __init__(self, app, port=5000, brain=None, allowed_cors_origin=False):
        """

        :param app: Flask API
        :param port: Port to listen
        :param brain: Brain object
        :type brain: Brain
        """
        super(FlaskAPI, self).__init__()
        self.app = app
        self.port = port
        self.brain = brain
        self.allowed_cors_origin = allowed_cors_origin

        # get current settings
        sl = SettingLoader()
        self.settings = sl.settings

        # api_response sent by the Order Analyser when using the /neurons/start/audio URL
        self.api_response = None
        # boolean used to notify the main process that we get the list of returned neuron
        self.order_analyser_return = False

        # configure the upload folder
        app.config['UPLOAD_AUDIO'] = AUDIO_UPLOAD_FOLDER
         # configure the upload folder
        app.config['UPLOAD_VIDEO'] = VIDEO_UPLOAD_FOLDER
        app.config['UPLOAD_FAIL'] = FAIL_UPLOAD_FOLDER
        # create the temp folder
        FileManager.create_directory(AUDIO_UPLOAD_FOLDER)
        FileManager.create_directory(VIDEO_UPLOAD_FOLDER)

        # Flask configuration remove default Flask behaviour to encode to ASCII
        self.app.url_map.strict_slashes = False
        self.app.config['JSON_AS_ASCII'] = False

        if self.allowed_cors_origin is not False:
            CORS(app, resources={r"/*": {"origins": allowed_cors_origin}}, supports_credentials=True)

        # no voice flag
        self.no_voice = False

        # Add routing rules
        self.app.add_url_rule('/', view_func=self.get_main_page, methods=['GET'])
        self.app.add_url_rule('/image', view_func=self.get_models, methods=['GET'])
        self.app.add_url_rule('/enhance', view_func=self.get_models, methods=['GET'])
        self.app.add_url_rule('/speech', view_func=self.get_models, methods=['GET'])
        #self.app.add_url_rule('/neurons/<neuron_name>', view_func=self.get_neuron, methods=['GET'])
        #self.app.add_url_rule('/neurons/start/id/<neuron_name>', view_func=self.run_neuron_by_name, methods=['POST'])
        self.app.add_url_rule('/speech/recognize', view_func=self.run_speech_recognition, methods=['POST'])
        self.app.add_url_rule('/image/<model_name>', view_func=self.run_image_by_model, methods=['POST'])
        #self.app.add_url_rule('/neurons/start/audio', view_func=self.run_neuron_by_audio, methods=['POST'])
        self.app.add_url_rule('/shutdown/', view_func=self.shutdown_server, methods=['POST'])

    def run(self):
        self.app.run(host='0.0.0.0', port="%s" % int(self.port), debug=True, threaded=True, use_reloader=False)

    @requires_auth
    def get_main_page(self):
        logger.debug("[FlaskAPI] get_main_page")
        data = {
            "Odie version": "%s" % version_str
        }
        return jsonify(data), 200

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def _get_neuron_by_name(self, neuron_name):
        """
        Find a neuron in the brain by its name
        :param neuron_name:
        :return:
        """
        all_neuron = self.brain.neurons
        for neuron in all_neuron:
            try:
                if neuron.name == neuron_name:
                    return neuron
            except KeyError:
                pass
        return None

    @requires_auth
    def get_models(self):
        """
        get all image models.
        test with curl:
        curl -i --user admin:secret  -X GET  http://127.0.0.1:5000/image
        """
        logger.debug("[FlaskAPI] get_models: all")

        models = [m for m in self.brain.neurons if m.cues == 'None']

        data = jsonify(neurons=[e.serialize() for e in models])
        return data, 200

    @requires_auth
    def get_neuron(self, neuron_name):
        """
        get a neuron by its name
        test with curl:
        curl --user admin:secret -i -X GET  http://127.0.0.1:5000/neurons/say-hello-en
        """
        logger.debug("[FlaskAPI] get_neuron: neuron_name -> %s" % neuron_name)
        neuron_target = self._get_neuron_by_name(neuron_name)
        if neuron_target is not None:
            data = jsonify(neurons=neuron_target.serialize())
            return data, 200

        data = {
            "neuron name not found": "%s" % neuron_name
        }
        return jsonify(error=data), 404

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @requires_auth
    def run_image_by_model(self, model_name):
        """
        Run a image model by its name
        test with curl:
        curl -i --user admin:secret -X POST  http://127.0.0.1:5000/image/caption

        :param model_name: name(id) of the model to execute
        :return:
        """
        logger.debug("[FlaskAPI] run_image_by_model: model_name name -> %s" % model_name)
        # get a neuron object from the name
        model_target = BrainLoader().get_brain()._get_neuron_by_name(name=model_name)

        # get parameters
        parameters = self.get_parameters_from_request(request)

        if model_target is None:
            data = {
                "model name not found": "%s" % model_name
            }
            return jsonify(error=data), 404

        # check if the post request has the file part
        uploaded_file = request.form['data']

        if not uploaded_file:
            data = {
                "error": "No file provided"
            }
            return jsonify(error=data), 400

        #uploaded_file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if uploaded_file.filename == '':
            data = {
                "error": "No file provided"
            }
            return jsonify(error=data), 400

        # save the file
        filename = secure_filename(uploaded_file.filename)
        base_path = os.path.join(self.app.config['VIDEO_UPLOAD_FOLDER'])
        uploaded_file.save(os.path.join(base_path, filename))
        # now start analyse the audio with STT engine
        video_path = base_path + os.sep + filename
        logger.debug("[FlaskAPI] run_image_by_model: with file path %s" % video_path)
        if not self.allowed_file(video_path):
            video_path = self._convert_to_wav(audio_file_path=video_path)
            
        #TODO: Call model selected
        #TODO: Call im2txt model for inference
        model = model_target.name()
        response = model.predict(video_path)

        data = jsonify(response)
        return data, 201



    @requires_auth
    def run_speech_recognition(self):
        """
        Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Odie Speech Recognition API.
        The Odie Speech Recognition API key is specified by ``key``. To obtain your own API key, contact the author at andrea.balzano@live.it
        The recognition language is determined by ``language``, an RFC5646 language tag like ``"en-US"`` (US English) or ``"fr-FR"`` (International French), defaulting to US English.

        Returns the most likely transcription if ``show_all`` is false (the default). Otherwise, returns the raw API response as a JSON dictionary.
        Test with curl
        curl -i --user admin:secret -H "Content-Type: audio/x-flac" -X POST -d '{"client":"odie","lang":"eng","key":"asdfg12345"}' http://localhost:5000/speech/recognise
        In case of quotes in the order or accents, use a file
        :return:
        """
        assert request.path == 'speech/recognise'
        assert request.method == 'POST'
        # check if the post request has the file part
        uploaded_file = request.form['data']

        if not uploaded_file:
            data = {
                "error": "No file provided"
            }
            return jsonify(error=data), 400

        #uploaded_file = request.files['file']
        # if user does not select file, browser also

        # save the file
        filename = secure_filename(uploaded_file.filename)
        base_path = os.path.join(self.app.config['AUDIO_UPLOAD_FOLDER'])
        uploaded_file.save(os.path.join(base_path, filename))
        # now start analyse the audio with STT engine
        audio_path = base_path + os.sep + filename
        logger.debug("[FlaskAPI] run_speech_recognition: with file path %s" % audio_path)
        if not self.allowed_file(audio_path):
            audio_path = self._convert_to_wav(audio_file_path=audio_path)

        #TODO: Call deepspeech2 model for inference
        model = BrainLoader().get_brain()._get_neuron_by_name(name='deepspeech2')
        response = model.predict(audio_path)
        
        if self.response is not None and self.response:
            data = jsonify(self.response)
            self.response = None
            logger.debug("[FlaskAPI] run_speech_recognition: data %s" % data)
            return data, 201
        else:
            data = {
                "error": "failed to process the given file"
            }
            return jsonify(error=data), 400

    

     @staticmethod
     def _convert_to_wav(audio_file_path):
        """
        If not already .wav, convert an incoming audio file to wav format. Using system avconv (raspberry)
        :param audio_file_path: the current full file path
        :return: Wave file path
        """
        # Not allowed so convert into wav using avconv (raspberry)
        base = os.path.splitext(audio_file_path)[0]
        extension = os.path.splitext(audio_file_path)[1]
        if extension != ".wav":
            current_file_path = audio_file_path
            audio_file_path = base + ".wav"
            os.system("avconv -y -i " + current_file_path + " " + audio_file_path)  # --> deprecated
            # subprocess.call(['avconv', '-y', '-i', audio_path, new_file_path], shell=True) # Not working ...
        return audio_file_path

    @requires_auth
    def shutdown_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()
        return "Shutting down..."
 
    @staticmethod
    def str_to_bool(s):
        if isinstance(s, bool):  # do not convert if already a boolean
            return s
        else:
            if s == 'True' or s == 'true' or s == '1':
                return True
            elif s == 'False' or s == 'false' or s == '0':
                return False
            else:
                return False
 
    @staticmethod
    def get_parameters_from_request(http_request):
        """
        Get "parameters" object from the
        :param http_request:
        :return:
        """
        parameters = None
        try:
            received_json = http_request.get_json(silent=False, force=True)
            if 'parameters' in received_json:
                parameters = received_json['parameters']
        except TypeError:
            pass
        logger.debug("[FlaskAPI] Overridden parameters: %s" % parameters)
 
        return parameters