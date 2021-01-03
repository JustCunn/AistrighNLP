#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import codecs

from .demutate_corpus import DemutateText
from .demutate_window import demutate_with_window
from .apply_mutations import MutateText
from .predict_inference import PredictText
from .utils import lowercase
from .bleu import celtic_bleu

from .demutate_corpus import create_parser as get_demutate_corpus_parser
from .demutate_window import create_parser as get_window_parser
from .apply_mutations import create_parser as get_apply_parser
from .predict_inference import create_parser as get_inference_parser
from .utils import lowercase_parser as get_lowercase_parser
from .bleu import create_parser as get_bleu_parser


def parse_args():

    args_parse = argparse.ArgumentParser()
    subparsers = args_parse.add_subparsers(dest='command',
                                           help="""Commands""")

    demutate_corpus_parser = get_demutate_corpus_parser(subparsers)
    window_parser = get_window_parser(subparsers)
    apply_parser = get_apply_parser(subparsers)
    inference_parser = get_inference_parser(subparsers)
    lowercase_parser = get_lowercase_parser(subparsers)
    bleu_parser = get_bleu_parser(subparsers)
    args = args_parse.parse_args()
    return args


def main():
    args = parse_args()

    if args.command == 'demutate-corpus':
        if args.input.name != '<stdin>':
            args.input = open(args.input.name, encoding='utf-8').readlines()

        demutation = DemutateText(args.language)
        demutation.demutate_corpus(args.input, args.output.name)

    elif args.command == 'demutate-window':
        if args.input.name != '<stdin>':
            args.input = open(args.input.name, encoding='utf-8').readlines()

        demutate_with_window(args.input, args.window, args.output.name, args.mask)

    elif args.command == 'apply-mutations':
        args.input = open(args.input.name, encoding='utf-8').readlines()
        if args.output.name != '<stdout>':
            args.output = codecs.open(args.output.name, 'w', encoding='utf-8')

        mutated = MutateText(args.language, skip_with_punc=args.skip)
        mutated.mutate_text(args.input, args.output.name)

    elif args.command == 'predict-mutations':
        if args.input.name != '<stdin>':
            args.input = open(args.input.name, encoding='utf-8').readlines()

        predictor = PredictText(args.language, args.data, args.window, args.mask, args.possible_labels,
                                args.vocab, args.labels, args.model)
        predictor.predict(args.input, args.output.name)

    elif args.command == 'lowercase':
        if args.input.name != '<stdin>':
            args.input = open(args.input.name, encoding='utf-8').readlines()

        lowercase(args.input, args.output.name)

    elif args.command == 'bleu':
        args.reference = open(args.reference.name, encoding='utf-8').readlines()

        args.predictions = open(args.predictions.name, encoding='utf-8').readlines()

        if args.demutated_reference:
            args.demutated_reference = open(args.demutated_reference.name, encoding='utf-8').readlines()

        celtic_bleu(args.reference, args.predictions, args.language, args.demutated_reference,
                    args.data, args.window, args.vocab, args.labels, args.model, args.mask, args.skip, args.output.name)
