#!/usr/bin/env python
# ----------------------------------------------------------------------------
# Copyright 2015-2016 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------

import os
import numpy as np
import pickle as pkl

from aeon.dataloader import DataLoader
from neon.backends import gen_backend
from neon.util.argparser import NeonArgparser, extract_valid_args
from neon.models import Model
from neon.data.dataloader_transformers import TypeCast, Retuple

from decoder import ArgMaxDecoder
from utils import get_predictions


def data_transform(dl):
    """ Data is loaded from Aeon as a 4-tuple. We need to cast the audio
    (index 0) from int8 to float32 and repack the data into (audio, 3-tuple).
    """

    dl = TypeCast(dl, index=0, dtype=np.float32)
    dl = Retuple(dl, data=(0,), target=(1, 2, 3))
    return dl

class DeepSpeechPredict(object):
    def __init__(self,model_file,file_path):

    if model_file is None:
        raise ArgumentError("A model file is required for evaluation")

    if file_path is None:
        raise ArgumentError("Please provide a file to predict")

    # Setup parameters for argmax decoder
    alphabet = "_'ABCDEFGHIJKLMNOPQRSTUVWXYZ "
    nout = len(alphabet)
    argmax_decoder = ArgMaxDecoder(alphabet, space_index=alphabet.index(" "))

    # Initialize our backend
    be = gen_backend(backend='gpu')

    # Setup dataloader
    eval_manifest = file_path
    if not os.path.exists(eval_manifest):
        raise IOError("Manifest file {} not found".format(eval_manifest))

    # Setup required dataloader parameters
    nbands = 13
    max_utt_len = 30
    max_tscrpt_len = 1300

    # Audio transformation parameters
    feats_config = dict(sample_freq_hz=16000,
                        max_duration="{} seconds".format(max_utt_len),
                        frame_length=".025 seconds",
                        frame_stride=".01 seconds",
                        feature_type="mfsc",
                        num_filters=nbands)

    # Transcript transformation parameters
    transcripts_config = dict(
        alphabet=alphabet,
        max_length=max_tscrpt_len,
        pack_for_ctc=True)

    # Initialize dataloader
    eval_cfg_dict = dict(type="audio,transcription",
                        audio=feats_config,
                        transcription=transcripts_config,
                        manifest_filename=eval_manifest,
                        macrobatch_size=be.bsz,
                        minibatch_size=be.bsz)
    eval_set = DataLoader(backend=be, config=eval_cfg_dict)
    eval_set = data_transform(eval_set)

    # Load the model
    model = Model(args.model_file)

    # Process data and compute stats
    return get_predictions(model, be, eval_set, argmax_decoder, nout)