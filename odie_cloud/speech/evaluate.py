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

from odie_cloud.speech.dataloader import make_loader
from neon.backends import gen_backend
from neon.models import Model

from odie_cloud.speech.decoder import ArgMaxDecoder
from odie_cloud.speech.utils import get_predictions


logging.basicConfig()
logger = logging.getLogger("odie")


class DeepSpeechPredict(object):
    '''
    the init function sets up the beckend so thatit is initialised at starting of the api and not each time it is called
    '''
    def __init__(self):
        logger.debug("[Deepspeech] init")

        # Setup parameters for argmax decoder
        self.alphabet = "_'ABCDEFGHIJKLMNOPQRSTUVWXYZ "
        self.nout = len(self.alphabet)
        logger.debug("[Deepspeech] setting decoder")
        self.argmax_decoder = ArgMaxDecoder(self.alphabet, space_index=self.alphabet.index(" "))

        logger.debug("[Deepspeech] Initialize gpu backend")
        # Initialize our backend
        try:
            self.be = gen_backend(backend='gpu')
        except:
            logger.debug("[Deepspeech] gpu backend failed")
            try:
                self.be = gen_backend(backend='mkl')
            except:
                logger.debug("[Deepspeech] mkl backend failed using basic cpu")
                self.be = gen_backend(backend='cpu')

    def GetProbs(self, model_file=None, file_path=None):
        '''
        get the translation from the model using model file and manifest file
        '''
        if model_file is None:
            raise Exception("A model file is required for evaluation")

        if file_path is None:
            raise Exception("Please provide a file to predict")

        # Setup dataloader
        logger.debug("[Deepspeech] manifest: {}".format(file_path))
        if not os.path.exists(file_path):
            logger.debug("[Deepspeech] Manifest file not found")
            raise IOError("Manifest file {} not found".format(file_path))

        # Setup required dataloader parameters
        nbands = 13
        max_utt_len = 30

        logger.debug("[Deepspeech] Setup dataloader")
        eval_set = make_loader(file_path, nbands, max_utt_len, backend_obj=self.be)

        # Load the model
        logger.debug("[Deepspeech] load model: {}".format(model_file))
        model = Model(model_file)

        # Process data and compute stats
        logger.debug("[Deepspeech] get predictions")
        return get_predictions(model, self.be, eval_set, self.argmax_decoder, self.nout)
