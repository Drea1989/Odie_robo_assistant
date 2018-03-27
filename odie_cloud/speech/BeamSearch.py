from __future__ import division
from __future__ import print_function
import logging
from autocorrect import spell
from odie_cloud.speech.decoder import Decoder
import math


logging.basicConfig()
logger = logging.getLogger("odie")


class BeamEntry:
    "information about one single beam at specific time-step"
    def __init__(self):
        self.prTotal = 0  # blank and non-blank
        self.prNonBlank = 0  # non-blank
        self.prBlank = 0  # blank
        self.y = ()  # labelling at current time-step


class BeamState:
    "information about beams at specific time-step"
    def __init__(self):
        self.entries = {}

    def norm(self):
        "length-normalise probabilities to avoid penalising long labellings"
        for (k, v) in self.entries.items():
            labellingLen = len(self.entries[k].y)
            self.entries[k].prTotal = self.entries[k].prTotal*(1.0/(labellingLen if labellingLen else 1))

    def sort(self):
        "return beams sorted by probability"
        u = [v for (k, v) in self.entries.items()]
        s = sorted(u, reverse=True, key=lambda x: x.prTotal)
        return [x.y for x in s]


class CtcBeamSearch(Decoder):

    def addLabelling(self, beamState, y):
        "adds labelling if it does not exist yet"
        if y not in beamState.entries:
            beamState.entries[y] = BeamEntry()

    def lm_words(self, sentence):
        words = ['<s>'] + sentence.split() + ['</s>']
        probs = 0
        for i, (prob, length, oov) in enumerate(self.LM.full_scores(sentence)):
            logger.debug("[CtcBeamSearch] LM prob {0} length {1}: {2}".format(prob, length, ' '.join(words[i+2-length:i+2])))
            score_multiplier = 1.1
            if oov:
                logger.debug('[CtcBeamSearch] \t"{0}" is an OOV'.format(words[i+1]))
                score_multiplier = 0.1
            probs += math.pow(10.0, prob)*score_multiplier
            logger.debug('[CtcBeamSearch] probs: {} score multiplier: {}'.format(probs, score_multiplier))
        return probs

    def calcExtPr(self, k, y, t, mat, beamState, classes):
        "probability for extending labelling y to y+k"

        # language model (kenlm 5-gram)
        sentence = ""
        for char in y:
            sentence = sentence + str(classes[char])
        sentence = sentence + str(classes[k])
        sentence = sentence.replace("_", "").lower()
        logger.debug("[CtcBeamSearch] ngram to score: {}".format(sentence))
        LmProb = self.lm_words(sentence)
        if len(y) and y[-1] == k:
            prb = mat[t, k]*beamState.entries[y].prBlank*LmProb
            logger.debug("[CtcBeamSearch] blank score: {0:.15f}".format(prb))
            return prb
        else:
            prb = mat[t, k]*beamState.entries[y].prTotal*LmProb
            logger.debug("[CtcBeamSearch] prTotal score: {0:.15f}".format(prb))
            return prb

    def decode(self, mat, classes):
        "beam search similar to algorithm described by Hwang"
        "Hwang - Character-Level Incremental Speech Recognition with Recurrent Neural Networks"

        blankIdx = self.blank_index
        maxT, maxC = mat.shape
        beamWidth = 3

        # Initialise beam state
        last = BeamState()
        y = ()
        last.entries[y] = BeamEntry()
        last.entries[y].prBlank = 1
        last.entries[y].prTotal = 1

        # go over all time-steps
        for t in range(maxT):
            curr = BeamState()

            # get best labellings
            BHat = last.sort()[0:beamWidth]

            # go over best labellings

            for y in BHat:
                prNonBlank = 0.0
                # if nonempty labelling
                if len(y) > 0:
                    # seq prob so far and prob of seeing last label again
                    prNonBlank = last.entries[y].prNonBlank*mat[t, y[-1]]

                # calc likelihood
                prBlank = last.entries[y].prTotal*mat[t, blankIdx]

                # save result
                self.addLabelling(curr, y)
                curr.entries[y].y = y
                curr.entries[y].prNonBlank += prNonBlank
                curr.entries[y].prBlank += prBlank
                curr.entries[y].prTotal += prBlank+prNonBlank

                # extend current labelling
                for k in range(maxC):
                    newY = y+(k,)
                    prNonBlank = self.calcExtPr(k, y, t, mat, last, classes)

                    # save result
                    self.addLabelling(curr, newY)
                    curr.entries[newY].y = newY
                    curr.entries[newY].prNonBlank += prNonBlank
                    curr.entries[newY].prTotal += prNonBlank
            # set new beam state
            last = curr
        # normalise probabilities according to labelling length
        last.norm()

        # sort by probability
        bestLabelling = last.sort()[0]  # get most probable labelling

        # map labels to chars
        res = ''
        for l in bestLabelling:
            res += classes[l]

        logger.debug("[ctcBeamSearch] output: {}".format(res))
        string = self.process_string(res, remove_repetitions=False)
        logger.debug("[ctcBeamSearch] string: {}".format(string))
        correct = ''
        for word in string.split():
            correct = correct + spell(word) + ' '
        logger.debug("[ctcBeamSearch] autocorrect: {}".format(correct))
        return correct.rstrip()
