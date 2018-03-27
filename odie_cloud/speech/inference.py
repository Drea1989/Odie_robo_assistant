import os
import logging
import tempfile
import numpy as np

from neon.backends import gen_backend
from neon.models import Model
from odie_cloud.speech.DataLoader import make_inference_loader
from odie_cloud.speech.BeamSearch import CtcBeamSearch


logging.basicConfig()
logger = logging.getLogger("odie")


class Inference(object):
    def __init__(self, model_file):
        logger.debug("[DeepSpeech] initializing")
        self.alphabet = "_'ABCDEFGHIJKLMNOPQRSTUVWXYZ "
        self.nout = len(self.alphabet)
        self.batch_size = 1
        self.model_file = model_file
        self.beam_search_decoder = CtcBeamSearch(self.alphabet, space_index=self.alphabet.index(" "))

    def softmax(self, x):
        return (np.reciprocal(np.sum(
                np.exp(x - np.max(x, axis=0)), axis=0)) *
                np.exp(x - np.max(x, axis=0)))

    def get_outputs(self, model, be, inputs, nout):
        outputs = model.fprop(inputs, inference=True)
        return self.softmax(outputs.get()).reshape(
            (nout, -1, be.bsz)).transpose((2, 0, 1))

    def predict_beam(self, audio_files):
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
        try:
            for file in eval_set:
                audio = file[0]
                audio_len = file[1]
                logger.debug("[DeepSpeech] predicting")
                output = self.get_outputs(model, model.be, audio, self.nout)
                strided_tmax = output.shape[-1]
                logger.debug("[DeepSpeech] adjusting output")
                utt_lens = strided_tmax * audio_len.get().ravel() / 100
                logger.debug("[DeepSpeech] transcripting with BeamSearch LM")
                out = output[0, :, :int(utt_lens[0])]
                probs_t_c = np.transpose(out, (1, 0))
                transcript = self.beam_search_decoder.decode(probs_t_c, self.alphabet)
        except:
            return 'error" model failed'
        finally:
            be.cleanup_backend()
            be = None
        return transcript

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

        try:
            for file in eval_set:
                audio = file[0]
                audio_len = file[1]
                logger.debug("[DeepSpeech] predicting")
                output = self.get_outputs(model, model.be, audio, self.nout)
                strided_tmax = output.shape[-1]
                logger.debug("[DeepSpeech] adjusting output")
                utt_lens = strided_tmax * audio_len.get().ravel() / 100
                logger.debug("[DeepSpeech] transcripting with ArgMaxDecoder")
                transcript = self.argmax_decoder.decode(output[0, :, :int(utt_lens[0])])
        except:
            return 'error" model failed'
        finally:
            be.cleanup_backend()
            be = None
        # spell = Corrector()
        # logger.debug("[DeepSpeech] transcript pre spell check: {}".format(transcript))
        # new_transcript = spell.correction(spell.word(transcript))
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
