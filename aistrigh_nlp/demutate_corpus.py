#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Justin Cunningham

"""
Demutates a given corpus.
Either returns the corpus to be used in Machine Translation or return the demutated corpus list and each tokens' label
"""
import re
import sys
import argparse


def create_parser(subparsers=None):

    if subparsers:
        parser = subparsers.add_parser('demutate-corpus',
                                       description="Demutate corpus")
    else:
        parser = argparse.ArgumentParser('demutate-corpus',
                                         description="Demutate corpus")

    parser.add_argument(
        '--input', '-i', type=argparse.FileType('r'), default=sys.stdin,
        metavar='PATH',
        help='Text to demutate'
    )
    parser.add_argument(
        '--output', '-o', type=argparse.FileType('w'), default=sys.stdout,
        metavar='PATH',
        help='Output for demutated corpus'
    )
    parser.add_argument(
        '--language', '-l', type=str,
        metavar='LANGUAGE',
        help='Language of text you wish to demutate'
    )


class DemutateText:
    def __init__(self, language):
        self.language = language

    def demutate_corpus(self, input_text, output_file=None):
        """Returns a demutated corpus
        :param input_text: File Path to your corpus file
        :param output_file: File Path to your demutated corpus file
        :return: Demutated corpus
        """

        f = input_text
        corp_list = []
        label_list = []

        if (self.language == 'ga') or (self.language == 'gd'):
            demutate = self.irish_scots
        else:
            raise Exception('{} is not a valid language choice'.format(self.language))

        if not isinstance(f, list):
            f = [f]

        for sentence in f:
            corpus_item, labels = demutate(sentence)
            corp_list.append(' '.join(corpus_item))
            label_list.extend(labels)

        if output_file:
            if output_file == '<stdout>':
                print(corp_list)
            else:
                with open(output_file, 'w') as out:
                    for item in corp_list:
                        out.write(item + '\n')
        else:
            return corp_list, label_list

    def irish_scots(self, sentence):
        tmp_label_list = []
        tmp_list = []
        label = ''
        for token in sentence.split():
            try:
                if token[:3] == 'bhf':  # If begins with 'bhf', remove 'bhf'
                    token = re.sub("^bh", "", token)  # Replaces 'bhf' with nothing (removes it)
                    label = 'uru'

                elif token[1] == 'h':  # If there's a séimhiú, remove it
                    token = list(token)  # Convert to list
                    token.pop(1)  # Remove the séimhiú
                    token = ''.join(token)  # Join the list again to form a string
                    label = 'seimhiu'

                elif token[:2] == 'h-':  # If the word contains a 'h-prothesis', remove it
                    token = re.sub('h-', '', token)
                    label = 'h'

                elif token[0] == 'h':  # Same as above, but tailored to Irish
                    if self.language == 'ga':
                        token = list(token)
                        token.pop(0)
                        token = ''.join(token)
                        label = 'h'

                elif token[:2] == 't-':  # If word contains 't-prothesis', remove it
                    token = re.sub('t-', '', token)
                    label = 't'

                elif token[:2] == 'ts':  # Same as above, but only remove the 't'
                    token = list(token)
                    token.pop(0)
                    token = ''.join(token)
                    label = 't'

                elif token[:2] == 'n-':  # If word contains 'eclipsis', remove it
                    token = re.sub('n-', '', token)
                    label = 'uru'

                elif token[:2] == 'mb' or token[:2] == 'nd' or token[:2] == 'gc' or token[:2] == 'ng' or \
                        token[:2] == 'dt' or token[:2] == 'bp':  # Same as above, but only remove the urú
                    if self.language == 'ga':
                        token = list(token)
                        token.pop(0)
                        token = ''.join(token)
                        label = 'uru'

                else:  # Case for non-mutated word
                    label = 'none'
            except IndexError:  # Handle index errors in for the séimhiú case
                pass

            if len(token) < 1:  # If word ends up being removed, skip it
                continue
            tmp_label_list.append(label)
            tmp_list.append(token)

        return tmp_list, tmp_label_list
