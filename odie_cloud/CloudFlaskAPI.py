import logging
import os
import threading
from odie.core.Utils.FileManager import FileManager

from odie.core.ConfigurationManager import SettingLoader
from werkzeug.utils import secure_filename

from flask import jsonify
from flask import request
# from flask_restful import abort
from flask_cors import CORS

from odie.core.RestAPI.utils import requires_auth
from odie._version import version_str


# cloud Models requirements
import tensorflow as tf
from odie_cloud.speech.inference import Inference
import math
import numpy as np
from odie_cloud.tensorflow_serving_client.client import TensorflowServingClient as TFClient
from odie_cloud.tensorflow_serving_client.protos import predict_pb2
from odie_cloud.tensorflow_serving_client.proto_util import copy_message
from odie_cloud.tensorflow_serving_client.caption_generator import Caption, TopN
from odie_cloud.tensorflow_serving_client import vocabulary


logging.basicConfig()
logger = logging.getLogger("odie")
try:
    os.environ["CUDA_VISIBLE_DEVICES"] = "1"
    logger.debug("[TensorflowSetUp] cuda device: {}".format(os.environ["CUDA_VISIBLE_DEVICES"]))
except:
    pass

'''
tensorflow serving configuration
model_config_list: {
                    config: {
                    name: "model1",
                    base_path: "/serving/models/model1",
                    model_platform: "tensorflow"},
                    config: {
                    name: "model2",
                    base_path: "/serving/models/model2",
                    model_platform: "tensorflow"}
                    }
/serving/bazel-bin/tensorflow_serving/model_servers/tensorflow_model_server --port=9000 --model_config_file=/serving/model_config/model_config.conf
'''
AUDIO_UPLOAD_FOLDER = '/tmp/odie_cloud/tmp_uploaded_audio'
VIDEO_UPLOAD_FOLDER = '/tmp/odie_cloud/tmp_uploaded_video'
FAIL_UPLOAD_FOLDER = '/tmp/odie_cloud/tmp_uploaded_failed_interactions'
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'jpg'}


class CloudFlaskAPI(threading.Thread):
    def __init__(self, app, port=5000, brain=None, allowed_cors_origin=False):
        """
        :param app: Flask API
        :param port: Port to listen
        :param brain: Brain object
        :type brain: Brain
        """
        super(CloudFlaskAPI, self).__init__()
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
        app.config['UPLOAD_VIDEO'] = VIDEO_UPLOAD_FOLDER
        app.config['UPLOAD_FAIL'] = FAIL_UPLOAD_FOLDER
        app.config['UPLOAD_AUDIO'] = AUDIO_UPLOAD_FOLDER
        # create the temp folder
        FileManager.create_directory(VIDEO_UPLOAD_FOLDER)
        FileManager.create_directory(FAIL_UPLOAD_FOLDER)
        FileManager.create_directory(AUDIO_UPLOAD_FOLDER)

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
        self.app.add_url_rule('/image/<model_name>', view_func=self.run_image_with_model, methods=['POST'])
        self.app.add_url_rule('/caption', view_func=self.run_caption, methods=['POST'])
        self.app.add_url_rule('/shutdown/', view_func=self.shutdown_server, methods=['POST'])
        self.app.add_url_rule('/speech/recognize', view_func=self.run_speech_recognition, methods=['POST'])

        logger.debug("[CloudFlaskAPI] getting OdieSTT model")
        for cl_object in self.settings.cloud:
            if cl_object.category == 'speech':
                speech_model = cl_object.parameters['model']
        self.dp = Inference(speech_model)

    def run(self):
        self.app.run(host='0.0.0.0', port="%s" % int(self.port), debug=True, threaded=True, use_reloader=False)

    @requires_auth
    def get_main_page(self):
        logger.debug("[CloudFlaskAPI] get_main_page")
        data = {
            "Odie Cloud Version": "%s" % version_str
        }
        return jsonify(data), 200

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @requires_auth
    def get_models(self):
        """
        get all image models.
        test with curl:
        curl -i --user admin:secret  -X GET  http://127.0.0.1:5000/image
        """
        logger.debug("[CloudFlaskAPI] get_models: all")
        models = []
        for cl_object in self.settings.cloud:
            models.append(cl_object.category)
        data = jsonify(models=[models])
        return data, 200

    @requires_auth
    def run_image_with_model(self, model_name):
        """
        Run an image model by its name
        test with curl:
        curl -i --user admin:secret -X POST  http://127.0.0.1:5000/image/caption

        :param model_name: name(id) of the model to execute
        :return:
        """
        logger.debug("[CloudFlaskAPI] run_image_by_model: model_name name -> %s" % model_name)
        assert request.method == 'POST'
        # check if the post request has the file part
        if 'file' not in request.files:
            logger.debug("[CloudFlaskAPI] no file in request.files")
            data = {
                "error": "No file provided"
            }
            return jsonify(error=data), 400

        uploaded_file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if uploaded_file.filename == '':
            logger.debug("[CloudFlaskAPI] filename == ''")
            data = {
                "error": "file non valid"
            }
            return jsonify(error=data), 400

        # get parameters
        # parameters = self.get_parameters_from_request(request)
        # logger.debug("[CloudFlaskAPI] run_image_by_model: request parameters %s" % parameters)

        # save the file
        filename = secure_filename(uploaded_file.filename)
        base_path = os.path.join(self.app.config['UPLOAD_VIDEO'])
        uploaded_file.save(os.path.join(base_path, filename))

        # now start analyse image with model
        video_path = base_path + os.sep + filename
        logger.debug("[CloudFlaskAPI] run_image_by_model: with file path %s" % video_path)
        if not self.allowed_file(video_path):
            data = {
                "image format not supported": "%s" % video_path
            }
            return jsonify(error=data), 404

        modelHost = "localhost"
        modelPort = 9000
        for cl_object in self.settings.cloud:
            if cl_object.category == model_name:
                modelHost = cl_object.parameters['TFhost']
                modelPort = cl_object.parameters['TFport']

        if modelHost is None or modelPort is None:
            data = {
                "model name not found": "%s" % model_name
            }
            return jsonify(error=data), 404

        tfclient = TFClient(modelHost, modelPort)
        with open(video_path, 'rb') as f:
            # See prediction_service.proto for gRPC request/response details.
            data = f.read()
            img_input = tf.contrib.util.make_tensor_proto(data, shape=[1])
        response = tfclient.make_prediction(input_data=img_input, input_tensor_name="image_feed:0", timeout=10, model_name=model_name)
        try:
            logger.debug("[CloudFlaskAPI] run_image_by_model prediction: {}".format(response))
        except:
            data = {
                "predicting": "exception"
            }
            base_path = os.path.join(self.app.config['UPLOAD_FAIL'])
            uploaded_file.save(os.path.join(base_path, filename))
            return jsonify(error=data), 404

        data = jsonify(response)
        return data, 201

    @requires_auth
    def run_caption(self):
        """
        Run an image model by its name
        test with curl:
        curl -i --user admin:secret -X POST  http://127.0.0.1:5000/image/caption

        :param model_name: name(id) of the model to execute
        :return:
        """
        logger.debug("[CloudFlaskAPI] run caption")
        assert request.method == 'POST'
        # check if the post request has the file part
        if 'file' not in request.files:
            logger.debug("[CloudFlaskAPI] no file in request.files")
            data = {
                "error": "No file provided"
            }
            return jsonify(error=data), 400

        uploaded_file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if uploaded_file.filename == '':
            logger.debug("[CloudFlaskAPI] filename == ''")
            data = {
                "error": "file non valid"
            }
            return jsonify(error=data), 400

        # save the file
        filename = secure_filename(uploaded_file.filename)
        base_path = os.path.join(self.app.config['UPLOAD_VIDEO'])
        uploaded_file.save(os.path.join(base_path, filename))

        # now start analyse image with model
        video_path = base_path + os.sep + filename
        logger.debug("[CloudFlaskAPI] caption: with file path %s" % video_path)
        if not self.allowed_file(video_path):
            data = {
                "image format not supported": "%s" % video_path
            }
            return jsonify(error=data), 404

        modelHost = "localhost"
        modelPort = 9000
        for cl_object in self.settings.cloud:
            if cl_object.category == 'caption':
                modelHost = cl_object.parameters['TFhost']
                modelPort = cl_object.parameters['TFport']

        if modelHost is None or modelPort is None:
            data = {
                "model name not found": "caption"
            }
            return jsonify(error=data), 404

        try:
            tfclient = TFClient(modelHost, modelPort)
            with open(video_path, 'rb') as f:
                # See prediction_service.proto for gRPC request/response details.
                data = f.read()
                img_input = tf.contrib.util.make_tensor_proto(data, shape=[])
            tfrequest = predict_pb2.PredictRequest()
            logger.debug("[CloudFlaskAPI] preparing request")
            tfrequest.model_spec.name = 'caption-part1'
            copy_message(img_input, tfrequest.inputs["in"])

            init = tfclient.execute(tfrequest, timeout=10)
            for key in init.outputs:
                tensor_proto = init.outputs[key]
                init_state = tf.contrib.util.make_ndarray(tensor_proto)
            # TODO: add vocab to settings
            logger.debug("[CloudFlaskAPI] preparing part2")
            vocab = vocabulary.Vocabulary('/home/drea/Odie_robo_assistant/odie_cloud/word_counts.txt')
            beam_size = 3
            max_caption_length = 20
            length_normalization_factor = 0.0
            initial_beam = Caption(sentence=[vocab.start_id],
                                   state=init_state[0],
                                   logprob=0.0,
                                   score=0.0,
                                   metadata=None)
            partial_captions = TopN(beam_size)
            partial_captions.push(initial_beam)
            complete_captions = TopN(beam_size)
            # Run beam search.
            logger.debug("[CloudFlaskAPI] Run beam search")
            for _ in range(max_caption_length - 1):
                partial_captions_list = partial_captions.extract()
                partial_captions.reset()
                input_feed = np.array([c.sentence[-1] for c in partial_captions_list])
                state_feed = np.array([c.state for c in partial_captions_list])
                input_feed = tf.contrib.util.make_tensor_proto(input_feed)
                state_feed = tf.contrib.util.make_tensor_proto(state_feed)
                # sending next sequence in
                tfrequest = predict_pb2.PredictRequest()
                tfrequest.model_spec.name = 'caption-part2'
                copy_message(input_feed, tfrequest.inputs["in"])
                copy_message(state_feed, tfrequest.inputs["state"])
                response = tfclient.execute(tfrequest, timeout=10)
                for key in response.outputs:
                    if key == 'softmax':
                        tensor_proto = response.outputs[key]
                        softmax = tf.contrib.util.make_ndarray(tensor_proto)
                    if key == 'state':
                        tensor_proto = response.outputs[key]
                        new_states = tf.contrib.util.make_ndarray(tensor_proto)
                for i, partial_caption in enumerate(partial_captions_list):
                    word_probabilities = softmax[i]
                    state = new_states[i]
                    # For this partial caption, get the beam_size most probable next words.
                    words_and_probs = list(enumerate(word_probabilities))
                    words_and_probs.sort(key=lambda x: -x[1])
                    words_and_probs = words_and_probs[0:beam_size]
                    # Each next word gives a new partial caption.
                    for w, p in words_and_probs:
                        if p < 1e-12:
                            logger.debug("[CloudFlaskAPI] avoiding log(0)")
                            continue  # Avoid log(0).
                        sentence = partial_caption.sentence + [w]
                        logprob = partial_caption.logprob + math.log(p)
                        score = logprob
                        if w == vocab.end_id:
                            if length_normalization_factor > 0:
                                score /= len(sentence)**length_normalization_factor
                            beam = Caption(sentence, state, logprob, score, None)
                            complete_captions.push(beam)

                        else:
                            beam = Caption(sentence, state, logprob, score, None)
                            partial_captions.push(beam)
                    if partial_captions.size() == 0:
                        # We have run out of partial candidates; happens when beam_size = 1.
                        break
                # If we have no complete captions then fall back to the partial captions.
                # But never output a mixture of complete and partial captions because a
                # partial caption could have a higher score than all the complete captions.
            logger.debug("[CloudFlaskAPI] beam seach completed")
            if not complete_captions.size():
                complete_captions = partial_captions
            captions = complete_captions.extract(sort=True)
            data = {}
            pred = {}
            # Ignore begin and end words.
            for i, caption in enumerate(captions):
                sentence = [vocab.id_to_word(w) for w in caption.sentence[1:-1]]
                sentence = " ".join(sentence)
                pred[sentence] = math.exp(caption.logprob)
                logger.debug("[CloudFlaskAPI] caption %d) %s (p=%f)" % (i, sentence, math.exp(caption.logprob)))
            data['result'] = pred
        except:
            data = {
                "result": "exception"
            }
            base_path = os.path.join(self.app.config['UPLOAD_FAIL'])
            uploaded_file.save(os.path.join(base_path, filename))
            return jsonify(error=data), 404

        data = jsonify(data)
        return data, 201

    @requires_auth
    def run_speech_recognition(self):
        """
        Performs speech recognition on ``audio_data`` (an ``AudioData`` instance), using the Odie Speech Recognition API.
        The Odie Speech Recognition API key is specified by ``key``. To obtain your own API key, contact the author at andrea.balzano@live.it
        The recognition language is determined by ``language``,
        an RFC5646 language tag like ``"en-US"`` (US English) or ``"fr-FR"`` (International French), defaulting to US English.

        Test with curl
        curl -i --user admin:secret -H "Content-Type: audio/x-flac" -X POST /
        -d '{"client":"odie","lang":"eng","key":"asdfg12345"}' http://localhost:5000/speech/recognize
        :return:
        """
        logger.debug("[CloudFlaskAPI] run_speech_recognition")
        assert request.path == '/speech/recognize'
        assert request.method == 'POST'
        # check if the post request has the file part
        if 'file' not in request.files:
            logger.debug("[CloudFlaskAPI] no file in request.files")
            data = {
                "error": "No file provided"
            }
            return jsonify(error=data), 400

        uploaded_file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if uploaded_file.filename == '':
            logger.debug("[CloudFlaskAPI] filename == ''")
            data = {
                "error": "file non valid"
            }
            return jsonify(error=data), 400
        # if user does not select file, browser also
        # save the file
        filename = secure_filename(uploaded_file.filename)
        base_path = os.path.join(self.app.config['UPLOAD_AUDIO'])
        audio_path = os.path.join(base_path, filename)
        # file_path = splitext(file_path)[0]+".wav"
        logger.debug("[CloudFlaskAPI] saving file to: {}".format(audio_path))
        uploaded_file.save(audio_path)
        if not self.allowed_file(audio_path):
            audio_path = self._convert_to_wav(audio_file_path=audio_path)

        logger.debug("[CloudFlaskAPI] calling deepspeech")
        try:
            response = self.dp.predict(audio_path)
            if response != "":
                data = {
                    "result": response
                }
                return jsonify(data), 201
            else:
                data = {"result": "predicted empty string"}
                base_path = os.path.join(self.app.config['UPLOAD_FAIL'])
                uploaded_file.save(os.path.join(base_path, filename))
                return jsonify(error=data), 404
        except Exception as e:
            data = {"result": str(e)}
            logger.error(e, exc_info=True)
            base_path = os.path.join(self.app.config['UPLOAD_FAIL'])
            uploaded_file.save(os.path.join(base_path, filename))
            return jsonify(error=data), 404

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
        logger.debug("[CloudFlaskAPI] Overridden parameters: %s" % parameters)

        return parameters
