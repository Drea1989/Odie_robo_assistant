#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import logging
import scipy.io.wavfile as wav
from deepspeech.model import Model
logging.basicConfig()
logger = logging.getLogger("odie")


class Speech(object):
    def __init__(self):
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

    def predict(self, audio_path):
        fs, audio = wav.read(audio_path)
        pred = self.ds.stt(audio, fs)
        logger.debug("[DeepSpeech] prediction: {}".format(pred))
        return pred
