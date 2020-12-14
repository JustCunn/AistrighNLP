#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Justin Cunningham


import pandas as pd
from tqdm import tqdm
import re
import sys
import argparse

from .demutate_corpus import demutate_corpus
from .utils import pad_sentence, add_window

reg = re.compile("[^a-záéíóú]")

def create_parser(subparsers=None):

    if subparsers:
        parser = subparsers.add_parser('demutate-window',
                                       description="creates a file with demutated tokens surrounded by a window of "
                                                   "tokens to be used in training")
    else:
        parser = argparse.ArgumentParser('demutate-window',
                                       description="creates a file with demutated tokens surrounded by a window of "
                                                   "tokens to be used in training")

    required = parser.add_argument_group('required arguments')
    required.add_argument(
        '--input', '-i', type=argparse.FileType('r'), default=sys.stdin,
        metavar='PATH', required=True,
        help='Input file'
    )
    parser.add_argument(
        '--output', '-o', type=argparse.FileType('w'), default=sys.stdout,
        metavar='PATH',
        help='Output file'
    )
    parser.add_argument(
        '--mask', '-m', type=str,
        metavar='STRING', default='<mask>',
        help='Mask Token (Default: <mask>)'
    )
    required.add_argument(
        '--window-length', '-w', type=int,
        metavar='VALUE', required=True,
        help='The amount of tokens on either side of the central token'
    )


def demutate_with_window(input_file, win_len, output_file=None, mask='<mask>'):
    """
    :param file_path: File Path to your corpus file
    :return: New file with target demutations with label
    """
    final = []
    corp_list = []
    label_list = []
    if not isinstance(input_file, list):
        input_file = [input_file]
    corp_list, label_list = demutate_corpus(input_file)

    for item in tqdm(corp_list):
        sentence = str(item)
        split_sent = sentence.split()
        zero_sentence_len = len(split_sent) - 1
        token_id = 0
        for token in split_sent:
            print(win_len)
            window, lsl, rsl = add_window(split_sent, token, win_len, token_id, zero_sentence_len)
            if len(window) != (2 * win_len) + 1:
                window = pad_sentence(window, win_len, lsl, rsl, mask)

            final.append(' '.join(window))
            token_id += 1

    df = pd.DataFrame(zip(final, label_list), columns=['sentence', 'label'])

    if output_file:
        df.to_csv(output_file, index=False)
    else:
        return df
