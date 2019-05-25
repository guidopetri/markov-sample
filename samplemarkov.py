#!/usr/bin/env python
# -*- coding: utf-8 -*-
# python 3.6.4

import random
import re
import json
import numpy


print("initializing")


class word():

    def __init__(self, initialDict=None, instanceCount=None):
        if initialDict is None and instanceCount is None:
            self.followDict = {}
            self.allInstances = 0
        else:
            self.followDict = initialDict
            self.allInstances = instanceCount
        return

    def addFollowingWord(self, newWord):
        try:
            count = self.followDict[newWord][0]
            self.allInstances += 1
            self.followDict[newWord] = (count + 1, count / self.allInstances)
        except KeyError:
            self.allInstances += 1
            self.followDict[newWord] = (1, 1 / self.allInstances)
        for each in self.followDict.keys():
            eachCount = self.followDict[each][0]
            self.followDict[each] = (eachCount, eachCount / self.allInstances)
        return

    def nextWord(self):
        # sumProb = sum([prob for (count,prob) in self.followDict.values()])
        # print(sumProb)
        if len(self.followDict) == 0:  # if the dictionary is empty
            return "."
        else:
            probs = [prob for (count, prob) in self.followDict.values()]
            return numpy.random.choice(list(self.followDict.keys()),
                                       p=probs)


def prepareJsonWrite(wordDict, initialWords):
    print("preparing json write")
    allData = {}
    allData['initialWords'] = initialWords
    allData['words'] = {}
    for key in wordDict.keys():
        try:
            test = allData['words'][key]
            print(test)
        except KeyError:
            allData['words'][key] = {}
        allData['words'][key]['nextWords'] = wordDict[key].followDict
        allData['words'][key]['instanceCount'] = wordDict[key].allInstances
    print("writing json to file")
    with open('savedWords.txt', 'w') as file:
        json.dump(allData, file)
    return


try:
    print("reading json file")
    with open('savedWords.txt', encoding='utf-8') as file:
        jsonData = json.loads(file.read())

    initialWords = jsonData['initialWords']

    wordDict = {}
    for key, value in jsonData['words'].items():
        wordDict[key] = word(initialDict=value['nextWords'],
                             instanceCount=value['instanceCount'])
except IOError:
    print("json file does not exist")
    wordDict = {}
    initialWords = []

    print("reading file")

    with open('sample.txt', encoding='utf-8') as file:
        text = file.read()

    print("creating word class instances")

    for wordMatch in re.finditer(r'\b[a-zA-Z]+?\b', text, re.IGNORECASE):
        try:
            test = wordDict[wordMatch.group(0).lower()]
        except KeyError:
            wordDict[wordMatch.group(0).lower()] = word()

    print("finding sentence start words")

    for startWord in re.finditer(r'\. \b([a-zA-Z]+?)\b', text):
        initialWords.append(startWord.group(1))

    print("finding next word probabilities")

    for key in wordDict.keys():
        regex_string = r'\b' + key + r'\b ?(\.|[a-zA-Z]+\b)'
        for match in re.finditer(regex_string, text, re.IGNORECASE):
            wordDict[str(key)].addFollowingWord(match.group(1))

    prepareJsonWrite(wordDict, initialWords)

print("generating markov sentence")

while True:
    randomWord = random.choice(initialWords)
    printList = [randomWord]

    while True:
        previousWord = printList[len(printList) - 1].lower()
        nextWord = wordDict[previousWord].nextWord()
        if nextWord == ".":
            break
        printList.append(nextWord)

    print("markov sentence:\n")
    print(" ".join(printList) + ".")
    choice = input("\ngenerate more? y/n\n")
    if choice == 'n':
        break
