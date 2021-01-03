#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Justin Cunningham

import re
import sys
import argparse


def create_parser(subparsers=None):

    if subparsers:
        parser = subparsers.add_parser('apply-mutations',
                                       description="Applies mutations supplied by predict-mutations")
    else:
        parser = argparse.ArgumentParser('apply-mutations',
                                         description="Applies mutations supplied by predict-mutations")
    parser.add_argument(
        '--input', '-i', type=argparse.FileType('r'),
        metavar='PATH',
        help='Input file'
    )
    parser.add_argument(
        '--output', '-o', type=argparse.FileType('w'), default=sys.stdout,
        metavar='PATH',
        help='Output file'
    )
    parser.add_argument(
        '--language', '-l', type=str,
        metavar='STRING',
        help='Language of text you wish to demutate'
    )
    parser.add_argument(
        '--skip', '-s', type=bool, default=True,
        metavar='BOOL',
        help="Don't mutate words containing punctuation [default: True]"
    )


reg = re.compile("[^a-záéíóú]")
vowel = re.compile("[aeiouáéíóú]")


class MutateText:
    def __init__(self, language, skip_with_punc=True):

        self.skip_with_punc = skip_with_punc
        self.language = language

    @staticmethod
    def get_label(sentence, idx, length):
        label = sentence[idx+length+1]
        return label

    @staticmethod
    def process_text(sentence):
        sentence = [x.strip().split("<<SEP>>") for x in sentence]
        for item in sentence:
            item.pop(-1)
        return sentence

    def mutate_text(self, text, output_file=None):
        if self.language == 'ga':
            applier = self.__apply_irish
        elif self.language == 'gd':
            applier = self.__apply_scots
        else:
            raise Exception('{} is not a valid language choice'.format(self.language))

        if not isinstance(text, list):
            text = [text]

        text = self.process_text(text)
        final_list = []
        for window in text:
            length = int(window[len(window)//2])
            output_item = applier(window, length)
            final_list.append(' '.join(output_item))

        if output_file:
            if output_file == '<stdout>':
                print(final_list)
            else:
                with open(output_file, 'w') as out:
                    for line in final_list:
                        out.write(line+'\n')
        else:
            return final_list

    def __apply_irish(self, window, length):
        temp_list = []
        for idx, token in enumerate(window[:length]):
            label = self.get_label(window, idx, length)
            if reg.search(token) and self.skip_with_punc:
                temp_list.append(token)
            elif label == 'none':
                temp_list.append(token)
            elif label == 'seimhiu':
                token = list(token)
                if vowel.search(token[0]):
                    temp_list.append(''.join(token))
                else:
                    token.insert(1, 'h')
                    token = ''.join(token)
                    temp_list.append(token)
            elif label == 'h':
                if not vowel.search(list(token)[0]):
                    temp_list.append(token)
                else:
                    token = list(token)
                    token.insert(0, 'h')
                    token = ''.join(token)
                    temp_list.append(token)
            elif label == 't':
                if vowel.search(list(token)[0]):
                    token = list(token)
                    token.insert(0, 't-')
                    token = ''.join(token)
                    temp_list.append(token)
                elif list(token)[0] == 's' or list(token)[0] == 'S':
                    token = list(token)
                    token.insert(0, 't')
                    token = ''.join(token)
                    temp_list.append(token)
                else:
                    temp_list.append(token)
            elif label == 'uru':
                token = list(token)
                if token[0] == 'b':
                    token.insert(0, 'm')
                    token = ''.join(token)
                    temp_list.append(token)
                elif token[0] == 'd':
                    token.insert(0, 'n')
                    token = ''.join(token)
                    temp_list.append(token)
                elif token[0] == 't':
                    token.insert(0, 'd')
                    token = ''.join(token)
                    temp_list.append(token)
                elif token[0] == 'c':
                    token.insert(0, 'g')
                    token = ''.join(token)
                    temp_list.append(token)
                elif token[0] == 'g':
                    token.insert(0, 'n')
                    token = ''.join(token)
                    temp_list.append(token)
                elif token[0] == 'p':
                    token.insert(0, 'b')
                    token = ''.join(token)
                    temp_list.append(token)
                elif token[0] == 'f':
                    token.insert(0, 'bh')
                    token = ''.join(token)
                    temp_list.append(token)
                elif vowel.search(token[0]):
                    if len(token) <= 1:
                        temp_list.append(''.join(token))
                    else:
                        token.insert(0, 'n-')
                        token = ''.join(token)
                        temp_list.append(token)
                else:
                    temp_list.append(''.join(token))

        return temp_list

    def __apply_scots(self, window, length):
        temp_list = []
        for idx, token in enumerate(window[:length]):
            label = self.get_label(window, idx, length)
            if reg.search(token) and self.skip_with_punc:
                temp_list.append(token)
            elif label == 'none':
                temp_list.append(token)
            elif label == 'seimhiu':
                token = list(token)
                if vowel.search(token[0]):
                    temp_list.append(''.join(token))
                else:
                    token.insert(1, 'h')
                    token = ''.join(token)
                    temp_list.append(token)
            elif label == 'h':
                if not vowel.search(list(token)[0]):
                    temp_list.append(token)
                else:
                    token = list(token)
                    token.insert(0, 'h-')
                    token = ''.join(token)
                    temp_list.append(token)
            elif label == 't':
                if vowel.search(list(token)[0]):
                    token = list(token)
                    token.insert(0, 't-')
                    token = ''.join(token)
                    temp_list.append(token)
                elif list(token)[0] == 's' or list(token)[0] == 'S':
                    token = list(token)
                    token.insert(0, 't')
                    token = ''.join(token)
                    temp_list.append(token)
                else:
                    temp_list.append(token)
            elif label == 'uru':
                token = list(token)
                if token[0] == 'f':
                    token.insert(0, 'bh')
                    token = ''.join(token)
                    temp_list.append(token)
                elif vowel.search(token[0]):
                    if len(token) <= 1:
                        temp_list.append(''.join(token))
                    else:
                        token.insert(0, 'n-')
                        token = ''.join(token)
                        temp_list.append(token)
                else:
                    temp_list.append(''.join(token))

        return temp_list
