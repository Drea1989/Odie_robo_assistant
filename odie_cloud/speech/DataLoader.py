import os
import numpy as np
import logging
from neon.data.aeon_shim import AeonDataLoader
from neon.data.dataloader_transformers import TypeCast, Retuple
logging.basicConfig()
logger = logging.getLogger("odie")


def inference_config(manifest_file, batch_size, nbands, max_utt_len):
    """ Aeon configuration for inference with only audio files"""

    audio_config = {"type": "audio",
                    "sample_freq_hz": 16000,
                    "max_duration": "{} seconds".format(max_utt_len),
                    "frame_length": "25 milliseconds",
                    "frame_stride": "10 milliseconds",
                    "feature_type": "mfsc",
                    "emit_length": True,
                    "num_filters": nbands}

    return {'manifest_filename': manifest_file,
            'manifest_root': os.path.dirname(manifest_file),
            'batch_size': batch_size,
            'block_size': batch_size,
            'etl': [audio_config, ]}


def wrap_dataloader(dl, target=True):
    """ Data is loaded from Aeon as a 4-tuple. We need to cast the audio
    (index 0) from int8 to float32 and repack the data into (audio, 3-tuple).
    """
    logger.debug("[DeepSpeech] recasting audio")
    dl = TypeCast(dl, index=0, dtype=np.float32)
    if target:
        dl = Retuple(dl, data=(0,), target=(2, 3, 1))
    return dl


def make_inference_loader(manifest_file, nbands, max_utt_len, backend_obj):
    aeon_config = inference_config(manifest_file, 1, nbands,
                                   max_utt_len)
    logger.debug("[DeepSpeech] preprocessing config with: {}".format(manifest_file))
    return wrap_dataloader(AeonDataLoader(aeon_config), target=False)
