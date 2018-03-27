import logging

import tensorflow as tf

from grpc.beta import implementations
from odie_cloud.tensorflow_serving_client.protos import predict_pb2
from odie_cloud.tensorflow_serving_client.protos import prediction_service_pb2
from odie_cloud.tensorflow_serving_client.proto_util import copy_message


logging.basicConfig()
logger = logging.getLogger("odie")


class TensorflowServingClient(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.channel = implementations.insecure_channel(self.host, self.port)
        self.stub = prediction_service_pb2.beta_create_PredictionService_stub(self.channel)

    def execute(self, request, timeout=10.0):
        return self.stub.Predict(request, timeout)

    def make_prediction(self, input_data, input_tensor_name, timeout=10.0, model_name=None, signature=None):
        request = predict_pb2.PredictRequest()
        logger.debug("[TFServing] preparing request")
        request.model_spec.name = model_name
        lstm = tf.contrib.util.make_tensor_proto(0., shape=[1024])
        # request.model_spec.signature_name = 'predict_images'
        # request.inputs[input_tensor_name].CopyFrom(input_data)
        copy_message(input_data, request.inputs[input_tensor_name])
        copy_message(lstm, request.inputs['lstm'])
        
        logger.debug("[TFServing] making prediction")
        response = self.execute(request, timeout=timeout)

        results = {}
        logger.debug("[TFServing] collecting array of outputs")
        for key in response.outputs:
            tensor_proto = response.outputs[key]
            nd_array = tf.contrib.util.make_ndarray(tensor_proto)
            results[key] = nd_array
        return results
