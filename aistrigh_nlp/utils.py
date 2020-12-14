#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Justin Cunningham

import re
import argparse
import sys

n_check = re.compile(r"^n[AEIOUÁÉÍÓÚ]")
h_check = re.compile(r"^h[AEIOUÁÉÍÓÚ]")

def lowercase_parser(subparsers=None):

    if subparsers:
        parser = subparsers.add_parser('lowercase',
                                       description="Applies mutations supplied by predict-mutations")
    else:
        parser = argparse.ArgumentParser('lowercase',
                                       description="Applies mutations supplied by predict-mutations")

    parser.add_argument(
        '--input', '-i', type=argparse.FileType('r'),
        metavar='PATH', required=True,
        help='Input file'
    )
    parser.add_argument(
        '--output', '-o', type=argparse.FileType('w'), default=sys.stdout,
        metavar='PATH',
        help='Output file'
    )


def lowercase(input_text, output=None):
    if not isinstance(input_text, list):
        input_text = input_text.split()
    lowercased_text = []
    for idx, line in enumerate(input_text):
        lowercased_text.append(line.split())
        for idx_token, token in enumerate(line.split()):
            if n_check.search(token):
                lowercased_text[idx][idx_token] = re.sub('^n', 'n-', token)
            elif h_check.search(token):
                lowercased_text[idx][idx_token] = re.sub('^h', 'h-', token)
        lowercased_text[idx] = ' '.join(lowercased_text[idx]).lower()

    if output:
        with open(output, 'w') as out:
            for line in lowercased_text:
                out.write(line)
    else:
        return lowercased_text


def pad_sentence(sentence, window_len, lsl, rsl, mask):
    """
    :param sentence: Sentence to pad
    :param window_len: The ammount of tokens in the desired sentence
    :param lsl: (left-side length) The current token count to the left of the central token
    :param rsl: (right-side length) The current token count to the right of the central token
    :param mask: The masking token
    :return: A sentence padded with BOS, EOS and MASK tokens
    """

    for i in range(window_len - lsl):
        sentence.insert(0, mask)

    for i in range(window_len - rsl):
        sentence.append(mask)

    return sentence


def add_window(sentence, token, window_len, token_id, zero_sentence_len):
    temp_list = []

    # Sort out former half of the data item
    if (token_id - window_len) < 0:
        temp_num = 0
        if token_id == 0:
            lsl = 0
            pass
        else:
            while temp_num < token_id:
                temp_list.append(sentence[temp_num])
                lsl = len(temp_list)
                temp_num += 1
    else:
        temp_num = (token_id - window_len)
        while temp_num != token_id:
            temp_list.append(sentence[temp_num])
            lsl = len(temp_list)
            temp_num += 1

    # Append token to be Predicted on
    temp_list.append(token)

    # Sort out latter half of the data item
    if (token_id + window_len) > zero_sentence_len:
        temp_num = zero_sentence_len
        list_len = len(temp_list)
        if token_id == zero_sentence_len:
            rsl = 0
            pass
        else:
            while temp_num > token_id:
                temp_list.insert(list_len, sentence[temp_num])
                rsl = len(temp_list) - (lsl + 1)
                temp_num -= 1
    else:
        temp_num = token_id + 1
        while temp_num < token_id + (window_len + 1):
            temp_list.append(sentence[temp_num])
            rsl = len(temp_list) - (lsl + 1)
            temp_num += 1

    return temp_list, lsl, rsl
