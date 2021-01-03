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
import sys
import pathlib

reg = re.compile("[^a-záéíóú]")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def create_parser(subparsers=None):

    if subparsers:
        parser = subparsers.add_parser('predict-mutations',
                                       description="Applies mutations supplied by predict-mutations")
    else:
        parser = argparse.ArgumentParser('predict-mutations',
                                         description="Applies mutations supplied by predict-mutations")

    parser.add_argument(
        '--data', '-d', type=str,
        metavar='PATH',
        help='Path to data folder'
    )
    parser.add_argument(
        '--input', '-i', type=argparse.FileType('r'), default=sys.stdin,
        metavar='PATH',
        help='Path to input file'
    )
    parser.add_argument(
        '--window', '-w', type=int,
        metavar='VALUE',
        help='Length of the window either side of the central token'
    )
    parser.add_argument(
        '--vocab', '-v', type=str,
        metavar='STR',
        help="Name of vocab file (If it is not 'vocab')"
    )
    parser.add_argument(
        '--labels', '-t', type=str,
        metavar='STR',
        help="Name of label file (If it is not 'labels')"
    )
    parser.add_argument(
        '--model', '-m', type=str,
        metavar='STR',
        help="Name of model file (If it is not the same as the folder name)"
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
    parser.add_argument(
        '--language', '-l', type=str,
        metavar='STRING',
        help='Language of text you wish to demutate'
    )
    parser.add_argument(
        '--possible-labels', '-c', nargs='+',
        metavar='LIST',
        help='List of the labels used in neural network (USE ONLY IF YOU USE A CUSTOM NETWORK)'
    )


class PredictText:
    def __init__(self, language, data_path, win_len, mask='<mask>', possible_labels=None,
                 vocab_name=None, label_name=None, model_name=None):
        """
        :param language: Language of the text
        :param data_path: Path to data folder containing vocab, label-vocab and model
        :param win_len: Window length (on each side)
        :param mask: Mask/Pad token
        :param possible_labels: List of labels used in custom neural network
        :param vocab_name: name of vocab file in data folder (if it's not 'vocab')
        :param label_name: name of label vocab file in data folder (if it's not 'labels')
        :param model_name: name of model in data folder (if it's not the same as the folder+'.pt')
        """

        self.language = language
        self.mask = mask
        self.win_len = win_len
        self.possible_labels = possible_labels
        self.model, self.vocabulary, self.labels = self.__load_model_and_vocab(data_path, model_name,
                                                                               vocab_name, label_name)

    def __load_model_and_vocab(self, data_path, model_name=None, vocab_name=None, label_name=None):
        if model_name:
            model = torch.jit.load(f'{data_path}/{model_name}.pt')
        else:
            model = torch.jit.load(f'{data_path}/{pathlib.PurePath(data_path).name}.pt')

        if vocab_name:
            with open(f'{data_path}/{vocab_name}', 'rb') as file:
                t_vocab = pickle.load(file)
        else:
            with open(f'{data_path}/vocab', 'rb') as file:
                t_vocab = pickle.load(file)

        if label_name:
            with open(f'{data_path}/{label_name}', 'rb') as file:
                l_vocab = pickle.load(file)
        else:
            with open(f'{data_path}/labels', 'rb') as file:
                l_vocab = pickle.load(file)

        vocabulary = data.Field()
        vocabulary.vocab = t_vocab

        labels = data.LabelField(dtype=torch.long)
        labels.vocab = l_vocab
        if self.possible_labels:
            label_list = [0 for _ in self.possible_labels]
            for i in self.possible_labels:
                label_list[labels.vocab[i]] = i
        elif self.language == 'ga':
            label_list = [0, 0, 0, 0, 0]
            for i in ['t', 'h', 'seimhiu', 'uru', 'none']:
                label_list[labels.vocab[i]] = i

        return model, vocabulary, label_list

    def category_from_list(self, output):
        """
        :param output: output from the network
        :return: The label with the highest probability from the network
        """

        out_list = []
        for tensor in output:
            top_n, top_index = tensor.topk(1)
            category_index = top_index[0].item()
            out_list.append(self.labels[category_index])
        return out_list[0]

    def inference(self, sentence):
        tok_sentence = [token for token in sentence]
        indexed = [[self.vocabulary.vocab.stoi[token]] for token in tok_sentence]
        input_tensor = torch.LongTensor(indexed).to(device)
        length = len(sentence)
        length_tensor = torch.LongTensor([length]).to(device)
        prediction = self.model(input_tensor, length_tensor).squeeze(1)
        prediction = self.category_from_list(prediction)
        return prediction

    def predict(self, input_text, output_file=None):
        """
        :param input_text: Text to predict mutations on
        :param output_file: Path to file to output predictions to
        :return: Predictions (in special format)
        """
        if not isinstance(input_text, list):
            input_text = [input_text]
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        corp_list = []
        token_list = []
        self.model.eval()

        for line in input_text:
            temp_token_list = []
            temp_corp_list = []
            sentence = str(line)
            split_sent = sentence.split()
            zero_sentence_len = len(split_sent) - 1

            for token_id, token in enumerate(split_sent):
                sequence, lsl, rsl = add_window(split_sent, token, self.win_len, token_id, zero_sentence_len)
                if len(sequence) != (2 * self.win_len) + 1:
                    sequence = pad_sentence(sequence, self.win_len, lsl, rsl, self.mask)
                temp_corp_list.append(sequence)
                temp_token_list.append(f'{token}<<SEP>>')
            temp_token_list.append(f'{len(temp_token_list)}<<SEP>>')
            corp_list.append(temp_corp_list)
            token_list.append(temp_token_list)

        final_list = []

        for window, t_list in zip(corp_list, token_list):
            for token_window in window:
                t_list.append(f'{self.inference(token_window)}<<SEP>>')
            final_list.append(''.join(t_list))

        if output_file:
            if output_file == '<stdout>':
                print(final_list)
            else:
                with open(output_file, 'w') as out:
                    for line in final_list:
                        out.write(line+'\n')
        else:
            return final_list
