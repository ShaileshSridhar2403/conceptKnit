# dependencies
from pyxdameraulevenshtein import damerau_levenshtein_distance
import fasttext
import numpy as np
from doublemetaphone import dm
from candidates import candidates

# built-in packages
from math import log
import json
import argparse
import os


class SpellingCorrection(object):

    def __init__(self, detection_list, language, model, k, backoff, pathtofrequencies, pathtomodel):
        """
        :param detection_list: list with tuples containing (misspelling, list of 10 left context tokens, list of 10 right context tokens)
        :param language: 1 if English, 0 if Dutch
        :param model: 1 if context-sensitive, 0 if noisy channel
        :param k: number of ranked corrections returned
        """
        # prepare model
        print('Initializing spelling correction model...')
        print(detection_list, len(detection_list[0]))
        assert len(detection_list[0]) == 3, 'Wrong input format'
        self.misspellings, self.left_contexts, self.right_contexts = zip(*detection_list)
        assert len(self.misspellings) == len(self.left_contexts) == len(self.right_contexts), 'Input data not properly synchronized'
        print(len(self.misspellings), 'misspellings to correct')
        self.ranking_model = model
        assert self.ranking_model in range(2), 'No valid correction model specified'
        assert k >= 1, 'No valid k specified'
        self.k = k
        self.backoff = backoff
        if language == 1:
            self.language = 'en'
        elif language == 0:
            self.language = 'nl'
        else:
            raise ValueError('No valid language input specified')

        # load embedding model and corpus frequencies
        with open(pathtofrequencies, 'r') as f:
            self.frequency_dict = json.load(f)
        self.model = fasttext.load_model(pathtomodel)
        print(dir(self.model))

        # set parameters for correction
        if self.language == "en":
            self.window_size = 9
            self.oov_penalty = 1.7
        elif self.language == "nl":
            self.window_size = 10
            self.oov_penalty = 2.4
        print('Model initialized')
        self.embeddings_index = {}
        f = open(os.path.join("..", 'glove.6B.300d.txt'))
        for line in f:
                values = line.split()
                word = values[0]
                coefs = np.asarray(values[1:], dtype='float32')
                self.embeddings_index[word] = coefs

    @staticmethod
    def comp_sum(vectors):
        """
        Composes a single vector representation out of several vectors using summing with reciprocal weighting.
        :param vectors: vectors to be composed
        :return: composed vector representation
        """
        weight_vector = np.reciprocal(np.arange(1., len(vectors) + 1))
        weighted_vectors = []
        for i, weight in enumerate(weight_vector):
            weighted_vectors.append(vectors[i] * weight)
        composed_vector = np.sum(weighted_vectors, axis=0)

        return composed_vector

    @staticmethod
    def normalize(vector):
        """
        Normalizes a vector.
        :param vector: a numpy array or list to normalize.
        :return: a normalized vector.
        """
        if not vector.any():
            return vector

        return vector / np.linalg.norm(vector)

    def vectorize(self, sequence, remove_oov=True):
        """
        :param sequence: sequence to be vectorized
        :param remove_oov: whether to vectorize oov tokens
        :return: vectorized sequence
        """
        print("vectorizing", sequence)
        if remove_oov:
            sequence = [x for x in sequence if x in self.model.words]

#        return [np.array(self.model[x]) for x in sequence]
        l = []
        for x in sequence:
                try:
                                l.append(self.normalize(np.array(self.embeddings_index[x])))
                except KeyError:
                                l.append(self.normalize(np.array(self.model[x])))
        return l

    def context_ranking(self, candidates_list):
        """
        Context-sensitive ranking model
        :param candidates_list: list of candidate list per misspelling
        :return: list with corrections or k-best corrections
        """
        correction_list = []

        for misspelling, left_context, right_context, candidates in zip(
                self.misspellings, self.left_contexts, self.right_contexts, candidates_list):

            if not candidates:
                correction_list.append('')
                continue

            left_context, right_context = left_context[::-1][:self.window_size], right_context[:self.window_size]
            left_window = self.vectorize(left_context, remove_oov=True)  # take only in-voc tokens for context
            right_window = self.vectorize(right_context, remove_oov=True)  # take only in-voc tokens for context
            # print("hello", left_window, right_window, left_context, "hey", right_context, "hey", self.left_contexts)
            if left_window:
                vectorized_left_window = self.comp_sum(left_window)
            else:
                # vectorized_left_window = np.zeros(len(self.model.dim))
                vectorized_left_window = np.zeros(300)

            if right_window:
                vectorized_right_window = self.comp_sum(right_window)
                print("hey there what is up", right_window)
            else:
                # vectorized_right_window = np.zeros(len(self.model.dim))
                vectorized_right_window = np.zeros(300)
#            print(candidates, "hello there", vectorized_left_window, vectorized_right_window, vectorized_left_window.any(), vectorized_right_window.any())
            print(type(vectorized_left_window))
            if not vectorized_left_window.any() or not vectorized_right_window.any():
                correction_list.append('')  # no context to correct the misspelling
                continue
            
            vectorized_context = self.normalize(np.sum((vectorized_left_window, vectorized_right_window), axis=0))
            print(vectorized_context.shape, vectorized_left_window.shape, vectorized_right_window.shape)
            print(vectorized_context[0], vectorized_left_window[0], vectorized_right_window[0])
            candidate_vectors = []
            oov_idxs = []

            # make vector representations of candidates
            for i, candidate in enumerate(candidates):
                # candidate_vectors.append(self.normalize(np.array(self.model[candidate])))
                try:
                                candidate_vectors.append(self.normalize(np.array(self.embeddings_index[candidate])))
                except KeyError:
                                candidate_vectors.append(self.normalize(np.array(self.model[candidate])))
                # if candidate not in self.model.words:
                #    oov_idxs.append(i)
                
            print("hello there")
            # calculate cosine similarities
            distances = [np.dot(vectorized_context, candidate) for candidate in candidate_vectors]
            spell_scores = [damerau_levenshtein_distance(misspelling, candidate)
                      for candidate in candidates]
            distances = [a / b for a, b in zip(distances, spell_scores)]
            for i, d in enumerate(distances):
                if i in oov_idxs:
                    distances[i] /= self.oov_penalty
            print("whatsup ", distances)
            # output
            if self.k == 1:
                try:
                    correction_list.append(candidates[np.argmax(distances)])
                except ValueError:
                    correction_list.append('')
                    print("Whats up bud")
            else:
                correction_list.append([candidates[i] for i in np.argsort(distances)[::-1][:self.k]])

        return correction_list

    def noisychannel_ranking(self, candidates_list):
        """
        An approximate implementation of the ranking method described in
        Lai et al. (2015), 'Automated Misspelling Detection and Correction in Clinical Free-Text Records'
        :param candidates_list: list of candidate list per misspelling
        :return: list with corrections or k-best corrections
        """
        correction_list = []
        count = 0
        for misspelling, candidates in zip(self.misspellings, candidates_list):
            count += 1
            print(count)
            if not candidates:
                correction_list.append('')
                continue

            score_list = []
            for candidate in candidates:
                orthographic_edit_distance = damerau_levenshtein_distance(misspelling, candidate)
                phonetic_edit_distance = damerau_levenshtein_distance(dm(misspelling)[0], dm(candidate)[0])
                spell_score = (2 * orthographic_edit_distance + phonetic_edit_distance) ** 2  # P(m|c)
                try:
                    frequency = self.frequency_dict[candidate]
                except KeyError:
                    frequency = 1
                frequency_score = 1 / (1 + log(frequency))  # P(c)
                score = spell_score * frequency_score  # P(c|m) = P(m|c)*P(c)
                score_list.append(score)

            score_list = np.array(score_list)
            if self.k == 1:
                try:
                    correction_list.append(candidates[np.argmin(score_list)])
                except ValueError:
                    correction_list.append('')
            else:
                correction_list.append([candidates[i] for i in np.argsort(score_list)[:self.k]])
                print(correction_list[-1])

        return correction_list

    def __call__(self):
        
        candidates_list = candidates(self.misspellings, self.language)
        print(candidates_list)
        if self.ranking_model:
            correction_list = self.context_ranking(candidates_list)
            if self.backoff:
                backoff_correction_list = self.noisychannel_ranking(candidates_list)
                for i, (correction, backoff_correction) in enumerate(zip(correction_list, backoff_correction_list)):
                    if not correction:
                        correction_list[i] = backoff_correction
        else:
            correction_list = self.noisychannel_ranking(candidates_list)

        return correction_list
                    

#########################################################
##################     EXECUTE     ######################
#########################################################

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-input', help='Input json file containing list of misspellings and contexts', dest='input', required=True, type=str)
    parser.add_argument('-output', help='Output file name to write correction list to', dest='output', required=True, type=str)
    parser.add_argument('-pathtofrequencies', help='Input json file containing dictionary with words as keys and corpus frequencies as values',
                            dest='pathtofrequencies', required=True, type=str)
    parser.add_argument('-pathtomodel', help='Input .bin file of trained fastText model',
                            dest='pathtomodel', required=True, type=str)
    parser.add_argument('-model', help='1 for context-sensitive, 0 for noisy channel', dest='model', default=1, type=int)
    parser.add_argument('-k', help='Number of top-ranked corrections to return', dest='k', default=1, type=int)
    parser.add_argument('-language', help='Language of the input, 1 for English, 0 for Dutch', dest='language', default=1, type=int)
    parser.add_argument('-backoff', help='Automatically backoff to noisy channel model if no context can be used, 1 if True, 0 if False', dest='backoff', default=0, type=int)
    args = parser.parse_args()
    with open(args.input, 'r') as f:
        detection_list = json.load(f)
    spelling_corrector = SpellingCorrection(detection_list, args.language, args.model, args.k, args.backoff, 
        args.pathtofrequencies, args.pathtomodel)
    corrections = spelling_corrector()
    print(corrections)
    with open(args.output + '.json', 'w') as f:
        json.dump(corrections, f)


