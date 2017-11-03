#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import logging
import scipy.io.wavfile as wav
from deepspeech.model import Model

import tensorflow as tf

from grpc.beta import implementations
from odie_cloud.tensorflow_serving_client.protos import prediction_service_pb2, predict_pb2
from odie_cloud.tensorflow_serving_client.proto_util import copy_message

logging.basicConfig()
logger = logging.getLogger("odie")


class TensorflowServingClient(object):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.channel = implementations.insecure_channel(self.host, self.port)
        self.stub = prediction_service_pb2.beta_create_PredictionService_stub(self.channel)
        BEAM_WIDTH = 500
        LM_WEIGHT = 2.15
        WORD_COUNT_WEIGHT = -0.10
        VALID_WORD_COUNT_WEIGHT = 1.10

        N_FEATURES = 26
        N_CONTEXT = 9
        # TODO: move this config to a file
        MODEL_PATH = "/home/drea/odie_cloud/keras/output_graph.pb"
        ALPHABET_CONFIG_PATH = "/home/drea/odie_cloud/tensorflow/DeepSpeech/data/alphabet.txt"
        LM_PATH = "/home/drea/odie_cloud/tensorflow/DeepSpeech/data/lm/lm.binary"
        TRIE_PATH = "/home/drea/odie_cloud/tensorflow/DeepSpeech/data/lm/trie"

        self.ds = Model(MODEL_PATH, N_FEATURES, N_CONTEXT, ALPHABET_CONFIG_PATH)

        if LM_PATH != "":
            logger.debug("[DeepSpeech] running with language model")
            self.ds.enableDecoderWithLM(ALPHABET_CONFIG_PATH, LM_PATH, TRIE_PATH, BEAM_WIDTH,
                                        LM_WEIGHT, WORD_COUNT_WEIGHT, VALID_WORD_COUNT_WEIGHT)

    def execute(self, request, timeout=10.0):
        return self.stub.Predict(request, timeout)

    def make_prediction(self, input_data, input_tensor_name, timeout=10.0, model_name=None):
        request = predict_pb2.PredictRequest()
        request.model_spec.name = model_name or 'model'

        copy_message(tf.contrib.util.make_tensor_proto(input_data), request.inputs[input_tensor_name])
        response = self.execute(request, timeout=timeout)

        results = {}
        for key in response.outputs:
            tensor_proto = response.outputs[key]
            nd_array = tf.contrib.util.make_ndarray(tensor_proto)
            results[key] = nd_array
        return results

    def speech_predict(self, audio_path):
        fs, audio = wav.read(audio_path)
        pred = self.ds.stt(audio, fs)
        logger.debug("[DeepSpeech] prediction: {}".format(pred))
        return pred
