#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Justin Cunningham


import pandas as pd
import re
import sys
import argparse

from .demutate_corpus import DemutateText
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
    parser.add_argument(
        '--input', '-i', type=argparse.FileType('r'), default=sys.stdin,
        metavar='PATH',
        help='Input file'
    )
    parser.add_argument(
        '--output', '-o', type=argparse.FileType('w'), default=sys.stdout,
        metavar='PATH',
        help='Output file'
    )
    parser.add_argument(
        '--mask', '-p', type=str,
        metavar='STRING', default='<mask>',
        help='Mask Token (Default: <mask>)'
    )
    parser.add_argument(
        '--language', '-l', type=str,
        metavar='STRING',
        help='Language of text you wish to demutate'
    )
    parser.add_argument(
        '--window', '-w', type=int,
        metavar='VALUE',
        help='The amount of tokens on either side of the central token'
    )


def demutate_with_window(input_text, win_len, language, output_file=None, mask='<mask>'):
    """Returns DF Object of demutated dataset
    :param input_text: Path to text file
    :param win_len: Length of the window on each side
    :param language: Language of the text
    :param output_file: Path to output file
    :param mask: Mask token
    :return: Create a dataframe object with dataset to train a new neural network
    """
    final = []
    if not isinstance(input_text, list):
        input_text = [input_text]
    demutation = DemutateText(language)
    corp_list, label_list = demutation.demutate_corpus(input_text)

    for item in corp_list:
        sentence = str(item)
        split_sent = sentence.split()
        zero_sentence_len = len(split_sent) - 1
        for token_id, token in enumerate(split_sent):
            window, lsl, rsl = add_window(split_sent, token, win_len, token_id, zero_sentence_len)
            if len(window) != (2 * win_len) + 1:
                window = pad_sentence(window, win_len, lsl, rsl, mask)

            final.append(' '.join(window))

    df = pd.DataFrame(zip(final, label_list), columns=['sentence', 'label'])

    if output_file:
        df.to_csv(output_file, index=False)
    else:
        return df
