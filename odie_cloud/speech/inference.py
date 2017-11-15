import logging
import os
import tempfile
import numpy as np

from tqdm import tqdm
from neon.backends import gen_backend
from neon.models import Model

from odie_cloud.speech.decoder import ArgMaxDecoder
from odie_cloud.speech.DataLoader import make_inference_loader
logging.basicConfig()
logger = logging.getLogger("odie")


class Inference(object):
    def __init__(self, model_file):
        logger.debug("[DeepSpeech] initializing")
        self.alphabet = "_'ABCDEFGHIJKLMNOPQRSTUVWXYZ "
        self.nout = len(self.alphabet)
        self.argmax_decoder = ArgMaxDecoder(self.alphabet, space_index=self.alphabet.index(" "))
        self.be = gen_backend('mkl', batch_size=1)
        self.batch_size = 1
        # Load the model
        self.model = Model(model_file)

    def softmax(self, x):
        return (np.reciprocal(np.sum(
                np.exp(x - np.max(x, axis=0)), axis=0)) *
                np.exp(x - np.max(x, axis=0)))

    def get_outputs(self, model, be, inputs, nout):
        # outputs = model.get_outputs_beam(inputs, num_beams=10)
        # testing beam search
        outputs = model.fprop(inputs, inference=True)
        return self.softmax(outputs.get()).reshape(
            (nout, -1, be.bsz)).transpose((2, 0, 1))
        # return outputs.get().reshape((nout, -1, be.bsz)).transpose((2, 0, 1))

    def predict(self, audio_files):
        eval_manifest = tempfile.mktemp(prefix="manifest_", suffix=".tsv")
        logger.debug("[DeepSpeech] calling dataloader")
        eval_set = self.setup_dataloader(audio_files, eval_manifest)
        if not self.model.initialized:
            logger.debug("[DeepSpeech] initializing")
            self.model.initialize(eval_set)

        for audio, audio_len in tqdm(eval_set, unit="files", total=eval_set.nbatches):
            logger.debug("[DeepSpeech] predicting")
            output = self.get_outputs(self.model, self.model.be, audio, self.nout)
            strided_tmax = output.shape[-1]
            logger.debug("[DeepSpeech] adjusting output")
            utt_lens = strided_tmax * audio_len.get().ravel() / 100
            for ii in range(self.be.bsz):
                logger.debug("[DeepSpeech] transcripting")
                transcript = self.argmax_decoder.decode(output[ii, :, :int(utt_lens[ii])])
        return transcript

    def setup_dataloader(self, audio_files, eval_manifest):
        with open(eval_manifest, "w") as fh:
            fh.write("@FILE\n")
            if not os.path.isfile(audio_files):
                raise IOError("Audio file does not exist: {}".format(audio_files))
            fh.write("{}\n".format(audio_files))
        # Setup required dataloader parameters
        nbands = 13
        max_utt_len = 30
        logger.debug("[DeepSpeech] manifest created")
        eval_set = make_inference_loader(eval_manifest, nbands, max_utt_len, backend_obj=self.be)
        return eval_set
