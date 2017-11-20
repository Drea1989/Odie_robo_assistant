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
import logging
import numpy as np
import Levenshtein as Lev
import math
import collections
from autocorrect import spell
import kenlm

logging.basicConfig()
logger = logging.getLogger("odie")


class Decoder(object):
    """
    Basic decoder class from which all other decoders inherit. Implements several
    helper functions. Subclasses should implement the decode() method.

    Arguments:
        alphabet (string): mapping from integers to characters.
        blank_index (int, optional): index for the blank '_' character. Defaults to 0.
        space_index (int, optional): index for the space ' ' character. Defaults to 28.
    """

    def __init__(self, alphabet, blank_index=0, space_index=1):
        # e.g. alphabet = "_'ABCDEFGHIJKLMNOPQRSTUVWXYZ#"
        self.alphabet = alphabet
        self.int_to_char = dict([(i, c) for (i, c) in enumerate(alphabet)])
        self.char_to_int = dict([(c, i) for (i, c) in enumerate(alphabet)])
        self.blank_index = blank_index
        self.space_index = space_index
        self.NEG_INF = -float("inf")

    def convert_to_string(self, sequence):
        "Given a numeric sequence, returns the corresponding string"

        return ''.join([self.int_to_char[i] for i in sequence])

    def process_string(self, sequence, remove_repetitions=False):
        """
        Given a string, removes blanks and replace space character with space.
        Option to remove repetitions (e.g. 'abbca' -> 'abca').

        Arguments:
            sequence (array of int): 1-d array of integers
            remove_repetitions (boolean, optional): If true, repeating characters
                are removed. Defaults to False.
        """
        string = ''

        for i, char in enumerate(sequence):
            if(char != self.int_to_char[self.blank_index]):
                # if this char is a repetition and remove_repetitions=true,
                # skip.
                if(remove_repetitions and i != 0 and char == sequence[i - 1]):
                    pass
                elif(char == self.alphabet[self.space_index]):
                    string = string + ' '
                else:
                    string = string + char

        return string

    def log_sum(self, list_of_probs):
        """
        Computes the sum of log-probabilities.

        Arguments:
            list_of_probs (iterable): list of log-probabilities
        """
        return np.log(np.sum([np.exp(p) for p in list_of_probs]))

    def wer(self, s1, s2):
        """
        Computes the Word Error Rate, defined as the edit distance between the
        two provided sentences after tokenizing to words.
        Arguments:
            s1 (string): space-separated sentence
            s2 (string): space-separated sentence
        """

        # build mapping of words to integers
        b = set(s1.split() + s2.split())
        word2char = dict(zip(b, range(len(b))))

        # map the words to a char array (Levenshtein packages only accepts
        # strings)
        w1 = [chr(word2char[w]) for w in s1.split()]
        w2 = [chr(word2char[w]) for w in s2.split()]

        return Lev.distance(''.join(w1), ''.join(w2))

    def cer(self, s1, s2):
        """
        Computes the Character Error Rate, defined as the edit distance.

        Arguments:
            s1 (string): space-separated sentence
            s2 (string): space-separated sentence
        """
        return Lev.distance(s1, s2)

    def decode(self, probs):
        """
        Given a matrix of character probabilities, returns the decoder's
        best guess of the transcription

        Arguments:
            probs (ndarray): Matrix of character probabilities, where probs[c,t]
                            is the probability of character c at time t
        Returns:
            string: sequence of the model's best guess for the transcription

        """
        raise NotImplementedError


class ArgMaxDecoder(Decoder):

    def decode(self, probs):
        """
        Returns the argmax decoding given the probability matrix. Removes
        repeated elements in the sequence, as well as blanks.
        """
        string = self.convert_to_string(np.argmax(probs, axis=0))
        string = self.process_string(string, remove_repetitions=True)
        logger.debug("[ArgMaxDecoder] string: {}".format(string))
        correct = ''
        for word in string.split():
            correct = correct + spell(word) + ' '
        logger.debug("[ArgMaxDecoder] autocorrect: {}".format(correct))
        return correct.rstrip()


class BeamLMDecoder(Decoder):
    """
    Beam-search decoder with character LM
    """
    def load_lm(self, lmfile):
        """
        Loads a language model from lmfile
        returns True if lm loading successful
        """
        self.lm = kenlm.LanguageModel(lmfile)
        logger.debug('[KENLM] {0}-gram model'.format(self.lm.order))
        return True

    def switch_dimentions(self, probs):
        new_probs = np.transpose(probs, (1, 0))
        logger.debug("[BeamLMDecoder] final shape: {}".format(new_probs.shape))
        return new_probs

    def make_new_beam(self):
        fn = lambda: (self.NEG_INF, self.NEG_INF)
        return collections.defaultdict(fn)

    def logsumexp(self, *args):
        """
        Stable log sum exp.
        """
        if all(a == self.NEG_INF for a in args):
            return self.NEG_INF
        a_max = max(args)
        lsp = math.log(sum(math.exp(a - a_max)
                           for a in args))
        return a_max + lsp

    def decode(self, probs, beam_size=40, blank=0):
        """
        Performs inference for the given output probabilities.
        Arguments:
          probs: The output probabilities (e.g. post-softmax) for each
            time step. Should be an array of shape (time x output dim).
          beam_size (int): Size of the beam to use during inference.
          blank (int): Index of the CTC blank label.
        Returns the output label sequence and the corresponding negative
        log-likelihood estimated by the decoder.
        """
        probs = self.switch_dimentions(probs)
        T, S = probs.shape
        probs = np.log(probs)

        # Elements in the beam are (prefix, (p_blank, p_no_blank))
        # Initialize the beam with the empty sequence, a probability of
        # 1 for ending in blank and zero for ending in non-blank
        # (in log space).
        beam = [(tuple(), (0.0, self.NEG_INF))]
        logger.debug("[BeamLMDecoder] looping over time")
        for t in range(T):  # Loop over time

            # A default dictionary to store the next step candidates.
            next_beam = self.make_new_beam()

            for s in range(S):  # Loop over vocab
                logger.debug("[BeamLMDecoder] looping over char: {}".format(s))
                p = probs[t, s]

                # The variables p_b and p_nb are respectively the
                # probabilities for the prefix given that it ends int a
                # blank and does not end in a blank at this time step.
                for prefix, (p_b, p_nb) in beam:  # Loop over beam

                    # If we propose a blank the prefix doesn't change.
                    # Only the probability of ending in blank gets updated.
                    if s == blank:
                        n_p_b, n_p_nb = next_beam[prefix]
                        n_p_b = self.logsumexp(n_p_b, p_b + p, p_nb + p)
                        next_beam[prefix] = (n_p_b, n_p_nb)
                        continue

                    # Extend the prefix by the new character s and add it to
                    # the beam. Only the probability of not ending in blank
                    # gets updated.
                    end_t = prefix[-1] if prefix else None
                    n_prefix = prefix + (s,)
                    n_p_b, n_p_nb = next_beam[n_prefix]
                    if s != end_t:
                        n_p_nb = self.logsumexp(n_p_nb, p_b + p, p_nb + p)
                    else:
                        # We don't include the previous probability of not ending
                        # in blank (p_nb) if s is repeated at the end. The CTC
                        # algorithm merges characters not separated by a blank.
                        n_p_nb = self.logsumexp(n_p_nb, p_b + p)

                    # *NB* this would be a good place to include an LM score.
                    next_beam[n_prefix] = (n_p_b, n_p_nb)

                    # If s is repeated at the end we also update the unchanged
                    # prefix. This is the merging case.
                    if s == end_t:
                        n_p_b, n_p_nb = next_beam[prefix]
                        n_p_nb = self.logsumexp(n_p_nb, p_nb + p)
                        next_beam[prefix] = (n_p_b, n_p_nb)

                    # Sort and trim the beam before moving on to the
                    # next time-step.
                    beam = sorted(next_beam.items(),
                                  key=lambda x: self.logsumexp(*x[1]),
                                  reverse=True)
                    beam = beam[:beam_size]

        best = beam[0]
        string = ''
        for idx in range(best):
            inte = int(best[idx])
            string = string.join(self.int_to_char[inte])
        return string
