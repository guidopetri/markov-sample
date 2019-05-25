#! /usr/bin/env python
# -*- coding: utf-8 -*-
# python 3.6.4

from random import choices
import re
import json
import os


class Word(object):

    def __init__(self, initial_dict=None, instances=None):
        self.follow_dict = initial_dict or {}
        self.all_instances = instances or 0

    def add_following_word(self, new_word):
        try:
            count = self.follow_dict[new_word]
            self.all_instances += 1
            self.follow_dict[new_word] = count + 1
        except KeyError:
            self.all_instances += 1
            self.follow_dict[new_word] = 1

    def next_word(self):
        if not self.follow_dict:  # if the dictionary is empty
            return ['.']
        else:
            probs = [count for count in self.follow_dict.values()]
            return choices(list(self.follow_dict.keys()),
                                weights=probs)


def save_markov_model(all_words, beginning_words):
    allData = {'beginning_words': beginning_words,
               'words': {},
               }

    for key in all_words.keys():
        if key not in allData['words']:
            allData['words'][key] = {}
        allData['words'][key]['next_words'] = all_words[key].follow_dict
        allData['words'][key]['instances'] = all_words[key].all_instances

    with open('markov_words.json', 'w') as f:
        json.dump(allData, f)


all_words = {}
if 'markov_words.json' in os.listdir():
    with open('markov_words.json', encoding='utf-8') as f:
        jsonData = json.load(f)

    beginning_words = jsonData['beginning_words']

    for key, value in jsonData['words'].items():
        all_words[key] = Word(initial_dict=value['next_words'],
                             instances=value['instances'])
else:
    beginning_words = []

    with open('sample.txt', encoding='utf-8') as f:
        text = f.read()

    for match in re.finditer(r'\b[a-zA-Z]+?\b', text, re.IGNORECASE):
        word = match.group(0).lower()
        if word not in all_words:
            all_words[word] = Word()

    for first_word in re.finditer(r'\. \b([a-zA-Z]+?)\b', text):
        beginning_words.append(first_word.group(1))

    for key in all_words.keys():
        regex_string = r'\b' + key + r'\b ?(\.|[a-zA-Z]+\b)'
        for match in re.finditer(regex_string, text, re.IGNORECASE):
            all_words[str(key)].add_following_word(match.group(1))

    save_markov_model(all_words, beginning_words)

while True:
    sentence = choices(beginning_words)

    next_word = ''
    while next_word != ['.']:
        prev_word = sentence[-1].lower()
        next_word = all_words[prev_word].next_word()
        sentence += next_word

    print("markov sentence:\n")
    print(' '.join(sentence))
    choice = input("\ngenerate more? y/n\n")
    if choice == 'n':
        break
