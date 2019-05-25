#! /usr/bin/env python
# -*- coding: utf-8 -*-
# python 3.6.4

import re
import json
from random import choices
from os import listdir


class Word(object):

    def __init__(self, initial_dict=None, instances=None):
        self.follow_dict = initial_dict or {}
        self.all_instances = instances or 0

    def add_following_word(self, new_word):
        self.follow_dict[new_word] = self.follow_dict.get(new_word, 0) + 1
        self.all_instances += 1

    def next_word(self):
        if not self.follow_dict:  # if the dictionary is empty
            return ['.']

        probs = [count for count in self.follow_dict.values()]
        return choices(list(self.follow_dict.keys()),
                       weights=probs)


def create_markov_model():
    beginning_words = []
    all_words = {}

    with open('sample.txt', encoding='utf-8') as f:
        text = f.read()

    for match in re.finditer(r'(?<=(. ))\b[a-zA-Z]+?\b', text, re.IGNORECASE):
        word = match.group(0).lower()
        if word not in all_words:
            all_words[word] = Word()
        if match.group(1) == '. ':  # if the group match is a period
            beginning_words.append(word.title())

    for key in all_words.keys():
        regex_string = r'\b' + key + r'\b ?(\.|[a-zA-Z]+\b)'
        for match in re.finditer(regex_string, text, re.IGNORECASE):
            all_words[key].add_following_word(match.group(1))
    return all_words, beginning_words


def save_markov_model(all_words, beginning_words):
    data = {'beginning_words': beginning_words,
            'words': {key: word.__dict__ for key,word in all_words.items()},
            }

    with open('markov_words.json', 'w') as f:
        json.dump(data, f)


def load_markov_model():
    with open('markov_words.json', encoding='utf-8') as f:
        data = json.load(f)

    beginning_words = data['beginning_words']
    all_words = {}

    for key, value in data['words'].items():
        all_words[key] = Word(initial_dict=value['follow_dict'],
                              instances=value['all_instances'])
    return all_words, beginning_words


if 'markov_words.json' in listdir():
    all_words, beginning_words = load_markov_model()
else:
    all_words, beginning_words = create_markov_model()
    save_markov_model(all_words, beginning_words)

for i in range(5):
    sentence = choices(beginning_words)

    while sentence[-1] != '.':
      # print(sentence)
        prev_word = sentence[-1].lower()
        next_word = all_words[prev_word].next_word()
        sentence += next_word

    print(' '.join(sentence[:-1]) + '.')
