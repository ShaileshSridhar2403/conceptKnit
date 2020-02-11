#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 12:19:57 2020

@author: shailesh
"""

import enchant
import random
from loadBillionWordsDataset import loadCorpusSentences

d = enchant.Dict("en_US")






def errorGenerate(word):
    word = word.lower()
    stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
    d = enchant.Dict("en_US")
    if not d.check(word) or word in stopwords or word.isdigit() or word[0].isupper():               #If word is already not in english dictionary, drop it//stopword//is number
        return None
    suggestions = d.suggest(word)
    
    if len(suggestions) > 1:
        random.shuffle(suggestions)
        return suggestions[0]
    else:
        return None                       #####If word has no similar word in dictinary return None

def insertErrorAtRandomPosition(sentence):
    words = sentence.split()
    wordsCopy = words
    
    randInd = random.randrange(0,len(wordsCopy))
    origWord = words[randInd]
    error = errorGenerate(origWord)
    
    while(not error and len(wordsCopy)!=1):
        wordsCopy.pop(randInd)
        randInd = random.randrange(0,len(wordsCopy))
        origWord = wordsCopy[randInd]
        error = errorGenerate(origWord)                     ###randomly pick a word in the sentence continuously until the pick has a similar word
    if len(wordsCopy) == 1:
        return (sentence,"No Malprop",-1)
    words[words.index(origWord)] = error
    errorSentence = ' '.join(words)                          
    
    return (sentence,errorSentence,randInd,error)


def sentencePairGeneration(sentenceList):
    tupleList = []
    ind = 0
    for sentence in sentenceList:
        print(ind)
        tupleList.append(insertErrorAtRandomPosition(sentence))
    return tupleList
 
    
#s = '''
#Because biographies of famous scientists tend to edit out their mistakes, we underestimate the degree of risk they were willing to take. And because anything a famous scientist did that wasn't a mistake has probably now become the conventional wisdom, those choices don't seem risky either.
#
#Biographies of Newton, for example, understandably focus more on physics than alchemy or theology. The impression we get is that his unerring judgment led him straight to truths no one else had noticed. How to explain all the time he spent on alchemy and theology? Well, smart people are often kind of crazy.
#
#But maybe there is a simpler explanation. Maybe the smartness and the craziness were not as separate as we think. Physics seems to us a promising thing to work on, and alchemy and theology obvious wastes of time. But that's because we know how things turned out. In Newton's day the three problems seemed roughly equally promising. No one knew yet what the payoff would be for inventing what we now call physics; if they had, more people would have been working on it. And alchemy and theology were still then in the category Marc Andreessen would describe as "huge, if true."
#
#Newton made three bets. One of them worked. But they were all risky.'''

#sentences =[sentence.strip() for sentence in  s.split('.') if len(sentence)>2]
sentences = loadCorpusSentences(100000)
corpus =sentencePairGeneration(sentences)
        

        
        
