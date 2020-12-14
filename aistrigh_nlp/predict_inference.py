#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Justin Cunningham

from .utils import pad_sentence, add_window

import re
import pickle
import torch
from torchtext import data
import torch.nn as nn
import torch
import argparse
from tqdm import tqdm
import sys

reg = re.compile("[^a-záéíóú]")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def create_parser(subparsers=None):

    if subparsers:
        parser = subparsers.add_parser('predict-mutations',
                                       description="Applies mutations supplied by predict-mutations")
    else:
        parser = argparse.ArgumentParser('predict-mutations',
                                       description="Applies mutations supplied by predict-mutations")

    required = parser.add_argument_group('required arguments')
    required.add_argument(
        '--model', '-m', type=argparse.FileType('r'),
        metavar='PATH', required=True,
        help='Path to model weights'
    )
    required.add_argument(
        '--input', '-i', type=argparse.FileType('r'), default=sys.stdin,
        metavar='PATH', required=True,
        help='Path to input file'
    )
    required.add_argument(
        '--window', '-w', type=int,
        metavar='VALUE', required=True,
        help='Length of the window either side of the central token'
    )
    required.add_argument(
        '--vocab', '-v', type=argparse.FileType('r'),
        metavar='PATH', required=True,
        help='Path to vocab file'
    )
    required.add_argument(
        '--labels', '-l', type=argparse.FileType('r'),
        metavar='PATH', required=True,
        help='Path to label file'
    )
    parser.add_argument(
        '--output', '-o', type=argparse.FileType('w'), default=sys.stdout,
        metavar='PATH',
        help='Path to output file'
    )
    parser.add_argument(
        '--mask', '-p', type=str, default='<mask>',
        metavar='STRING',
        help='Mask Token (Default: <mask>)'
    )


def load_vocab(vocab_file, label_file):
    with open(vocab_file, 'rb') as file:
        vocab = pickle.load(file)

    with open(label_file, 'rb') as file:
        l_vocab = pickle.load(file)

    VOCAB = data.Field()
    VOCAB.vocab = vocab

    LABEL = data.LabelField(dtype=torch.long)
    LABEL.vocab = l_vocab
    labeled_categories = [0,0,0,0,0]
    for i in ['t', 'h', 'seimhiu', 'uru', 'none']:
        labeled_categories[LABEL.vocab[i]] = i

    return VOCAB, labeled_categories

def load_model(model_path, model):
    model.load_state_dict(torch.load(model_path))
    model = model.to(device)

    return model


def category_from_list(output, categories):
    out_list = []
    for ten in output:
        top_n, top_i = ten.topk(1)
        category_i = top_i[0].item()
        out_list.append(categories[category_i])
    return out_list[0]


def inference(model, sentence, VOCAB, categories):
    tok_sentence = [token for token in sentence]
    indexed = [[VOCAB.vocab.stoi[token]] for token in tok_sentence]
    input_tensor = torch.LongTensor(indexed).to(device)
    length = len(sentence)
    length_tensor = torch.LongTensor([length]).to(device)
    prediction = model(input_tensor, length_tensor).squeeze(1)
    prediction = category_from_list(prediction, categories)
    return prediction


def predict(model_path, input_file, win_len, vocab_file, label_file, mask, output_file=None):

    if not isinstance(input_file, list):
        input_file = [input_file]

    VOCAB, labeled_cats = load_vocab(vocab_file, label_file)
    
    model = torch.jit.load(model_path)

    corp_list = []
    token_list = []

    for line in tqdm(input_file):
        temp_token_list = []
        temp_corp_list = []
        sentence = str(line)
        split_sent = sentence.split()
        token_id = 0
        zero_sentence_len = len(split_sent) - 1

        for token in split_sent:
            sequence, lsl, rsl = add_window(split_sent, token, win_len, token_id, zero_sentence_len)
            if len(sequence) != (2 * win_len) + 1:
                sequence = pad_sentence(sequence, win_len, lsl, rsl, mask)
            temp_corp_list.append(sequence)
            temp_token_list.append(f'{token}<<SEP>>')
            token_id += 1
        temp_token_list.append(f'{len(temp_token_list)}<<SEP>>')
        corp_list.append(temp_corp_list)
        token_list.append(temp_token_list)

    final_list = []

    for window, t_list in tqdm(zip(corp_list, token_list)):
        for token_window in window:
            t_list.append(f'{inference(model, token_window, VOCAB, labeled_cats)}<<SEP>>')
        final_list.append(''.join(t_list))

    if output_file:
        for line in final_list:
            output_file.write(line+'\n')
    else:
        return token_list
