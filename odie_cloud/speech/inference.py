import os
import logging
import tempfile
import numpy as np
from tqdm import tqdm

from neon.backends import gen_backend
from neon.models import Model
from odie_cloud.speech.decoder import ArgMaxDecoder
from odie_cloud.speech.DataLoader import make_inference_loader
import pycuda
logging.basicConfig()
logger = logging.getLogger("odie")


class Inference(object):
    def __init__(self, model_file):
        logger.debug("[DeepSpeech] initializing")
        self.alphabet = "_'ABCDEFGHIJKLMNOPQRSTUVWXYZ "
        self.nout = len(self.alphabet)
        self.batch_size = 1
        self.argmax_decoder = ArgMaxDecoder(self.alphabet, space_index=self.alphabet.index(" "))
        self.model_file = model_file

    def softmax(self, x):
        return (np.reciprocal(np.sum(
                np.exp(x - np.max(x, axis=0)), axis=0)) *
                np.exp(x - np.max(x, axis=0)))

    def get_outputs(self, model, be, inputs, nout):
        outputs = model.fprop(inputs, inference=True)
        return self.softmax(outputs.get()).reshape(
            (nout, -1, be.bsz)).transpose((2, 0, 1))

    def predict(self, audio_files):
        eval_manifest = tempfile.mktemp(prefix="manifest_", suffix=".tsv")
        logger.debug("[DeepSpeech] generating backend")
        try:
            be = gen_backend('gpu', batch_size=self.batch_size)
        except:
            logger.debug("[DeepSpeech] gpu backend failed, using mkl")
            be = gen_backend('mkl', batch_size=self.batch_size)
        logger.debug("[DeepSpeech] calling dataloader")
        eval_set = self.setup_dataloader(be, audio_files, eval_manifest)
        model = Model(self.model_file)
        if not model.initialized:
            logger.debug("[DeepSpeech] initializing")
            model.initialize(eval_set)

        #for audio, audio_len in tqdm(eval_set, unit="files", total=eval_set.nbatches):
        try:
            for file in eval_set:
                audio = file[0]
                audio_len = file[1]
                logger.debug("[DeepSpeech] predicting")
                output = self.get_outputs(model, model.be, audio, self.nout)
                strided_tmax = output.shape[-1]
                logger.debug("[DeepSpeech] adjusting output")
                utt_lens = strided_tmax * audio_len.get().ravel() / 100
                for ii in range(be.bsz):
                    logger.debug("[DeepSpeech] transcripting")
                    transcript = self.argmax_decoder.decode(output[ii, :, :int(utt_lens[ii])])
        except:
            return None
        finally:
            be.cleanup_backend()
            be = None
        return transcript

    def setup_dataloader(self, be, audio_files, eval_manifest):
        with open(eval_manifest, "w") as fh:
            fh.write("@FILE\n")
            if not os.path.isfile(audio_files):
                raise IOError("Audio file does not exist: {}".format(audio_files))
            fh.write("{}\n".format(audio_files))
        # Setup required dataloader parameters
        nbands = 13
        max_utt_len = 30
        logger.debug("[DeepSpeech] manifest created")
        eval_set = make_inference_loader(eval_manifest, nbands, max_utt_len, backend_obj=be)
        return eval_set
