#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Justin Cunningham

"""
Demutates a given corpus.
Either returns the corpus to be used in Machine Translation or return the demutated corpus list and each tokens' label
"""
import re
import sys
from tqdm import tqdm
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


corp_list = []
label_list = []


def demutate_corpus(file, output_file=None):
    """
    :param file_path: File Path to your corpus file
    :return: Demutated corpus
    """

    f = file
    label = ''
    for item in tqdm(f):
        sentence = str(item)  # Isolate the sentence so it's not part of an iterator
        tmp_list = []
        tmp_label_list =[]
        for token in item.split():
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
            label_list.append(label)
            tmp_list.append(token)

        corp_list.append(' '.join(tmp_list))

    if output_file:
        for item in corp_list:
            output_file.write(item + '\n')
    else:
        return corp_list, label_list
