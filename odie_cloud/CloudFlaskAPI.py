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


# cloud Models
from PIL import Image

logging.basicConfig()
logger = logging.getLogger("odie")
try:
    os.environ["CUDA_VISIBLE_DEVICES"] = "1"
    logger.debug("[TensorflowSetUp] cuda device: {}".format(os.environ["CUDA_VISIBLE_DEVICES"]))
except:
    pass
from odie_cloud.tensorflow_serving_client.client import TensorflowServingClient as TFClient

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
        # create the temp folder
        FileManager.create_directory(VIDEO_UPLOAD_FOLDER)
        FileManager.create_directory(FAIL_UPLOAD_FOLDER)

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
        self.app.add_url_rule('/shutdown/', view_func=self.shutdown_server, methods=['POST'])

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
        parameters = self.get_parameters_from_request(request)
        logger.debug("[CloudFlaskAPI] run_image_by_model: request parameters %s" % parameters)

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

        video_data = Image.open(video_path)

        modelHost = None
        modelPort = None
        # TODO: add settings config
        for cl_object in self.settings.cloud:
            if cl_object.category == model_name:
                modelHost = cl_object.parameters['tfhost']
                modelPort = cl_object.parameters['tfport']

        if modelHost is None or modelPort is None:
            data = {
                "model name not found": "%s" % model_name
            }
            return jsonify(error=data), 404

        tfclient = TFClient(modelHost, modelPort)
        try:
            response = tfclient.make_prediction(input_data=video_data, input_tensor_name="inputs", timeout=10, model_name=model_name)
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
