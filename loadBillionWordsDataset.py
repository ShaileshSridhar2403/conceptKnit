#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  9 23:50:25 2020

@author: shailesh

"""
import pandas as pd
def loadCorpusSentences(nLines):
    with open("/home/shailesh/Documents/Projects/finalProj/billion-word-imputation/train_v2.txt") as f:
        lineNo = 0
        sentences = []
        while lineNo < nLines:
            sentence = f.readline()
            sentences.append(sentence.strip())
            lineNo+=1
    return sentences

def saveAsCSV(tupleList):
    df = pd.DataFrame(tupleList, columns =['Original', 'Error Introduced', 'Error Index','Error']) 
    df.to_csv("data.csv", encoding='utf-8', index=False)
        
#	
#	df = pd.read_csv(trainPath)
#	sentences = list(df['sentence'])
#	return sentences
