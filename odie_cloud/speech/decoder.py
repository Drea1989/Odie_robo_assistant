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
