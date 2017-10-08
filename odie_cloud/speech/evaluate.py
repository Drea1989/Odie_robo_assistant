#!/usr/bin/env python3
# ----------------------------------------------------------------------------
# Copyright 2017 Andrea Balzano
# Licensed under the GNU Affero General Public License v3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.gnu.org/licenses
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
import logging
import os
import numpy as np

from aeon.dataloader import DataLoader
from neon.backends import gen_backend
from neon.models import Model
from neon.data.dataloader_transformers import TypeCast, Retuple

from odie_cloud.speech.decoder import ArgMaxDecoder
from odie_cloud.speech.utils import get_predictions


logging.basicConfig()
logger = logging.getLogger("odie")


def data_transform(dl):
    """ Data is loaded from Aeon as a 4-tuple. We need to cast the audio
    (index 0) from int8 to float32 and repack the data into (audio, 3-tuple).
    """

    dl = TypeCast(dl, index=0, dtype=np.float32)
    dl = Retuple(dl, data=(0,), target=(1, 2, 3))
    return dl


class DeepSpeechPredict(object):
    def __init__(self, model_file=None, file_path=None):
        logger.debug("[Deepspeech] init")

        if model_file is None:
            raise Exception("A model file is required for evaluation")

        if file_path is None:
            raise Exception("Please provide a file to predict")

        # Setup parameters for argmax decoder
        alphabet = "_'ABCDEFGHIJKLMNOPQRSTUVWXYZ "
        nout = len(alphabet)
        logger.debug("[Deepspeech] setting decoder")
        argmax_decoder = ArgMaxDecoder(alphabet, space_index=alphabet.index(" "))

        logger.debug("[Deepspeech] Initialize gpu backend")
        # Initialize our backend
        be = gen_backend(backend='gpu')

        # Setup dataloader
        logger.debug("[Deepspeech] get manifest")
        eval_manifest = file_path.lsplit('.', 1)[1]+".tsv"
        if not os.path.exists(eval_manifest):
            raise IOError("Manifest file {} not found".format(eval_manifest))

        # Setup required dataloader parameters
        nbands = 13
        max_utt_len = 30
        logger.debug("[Deepspeech] audio transform")
        # Audio transformation parameters
        feats_config = dict(sample_freq_hz=16000,
                            max_duration="{} seconds".format(max_utt_len),
                            frame_length=".025 seconds",
                            frame_stride=".01 seconds",
                            feature_type="mfsc",
                            num_filters=nbands)
        # Initialize dataloader
        eval_cfg_dict = dict(type="audio",
                             audio=feats_config,
                             manifest_filename=eval_manifest,
                             macrobatch_size=be.bsz,
                             minibatch_size=be.bsz)
        logger.debug("[Deepspeech] Setup dataloader")
        eval_set = DataLoader(backend=be, config=eval_cfg_dict)
        logger.debug("[Deepspeech] data transformation")
        eval_set = data_transform(eval_set)

        # Load the model
        logger.debug("[Deepspeech] load model: {}".format(model_file))
        model = Model(model_file)

        # Process data and compute stats
        logger.debug("[Deepspeech] get predictions")
        return get_predictions(model, be, eval_set, argmax_decoder, nout)
